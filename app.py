import boto3
import io
import zipfile
from flask import Flask, jsonify, request, send_file
from dotenv import load_dotenv
import os
import sqlite3
import bcrypt
from flask import Flask, jsonify, request, send_file, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Set a secret key for session management



# Load environment variables from .env file
load_dotenv()


# login prmpt 
# Add this function to handle authentication
def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return True
    return False

def add_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_user(username, password):
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "Invalid credentials", 401
    return render_template_string('''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.before_request
def require_login():
    if not session.get("logged_in"):
        if request.endpoint not in ["login", "static"]:
            return redirect(url_for("login"))


# Configuration for multiple S3 buckets
buckets = [
    {
        "name": os.getenv("S3_BUCKET_1"),
        "access_key": os.getenv("S3_ACCESS_KEY_1"),
        "secret_key": os.getenv("S3_SECRET_KEY_1"),
        "region": os.getenv("S3_REGION_1"),
    },
    {
        "name": os.getenv("S3_BUCKET_2"),
        "access_key": os.getenv("S3_ACCESS_KEY_2"),
        "secret_key": os.getenv("S3_SECRET_KEY_2"),
        "region": os.getenv("S3_REGION_2"),
    },
    {
        "name": os.getenv("S3_BUCKET_3"),
        "access_key": os.getenv("S3_ACCESS_KEY_3"),
        "secret_key": os.getenv("S3_SECRET_KEY_3"),
        "region": os.getenv("S3_REGION_3"),
    },
    {
        "name": os.getenv("S3_BUCKET_4"),
        "access_key": os.getenv("S3_ACCESS_KEY_4"),
        "secret_key": os.getenv("S3_SECRET_KEY_4"),
        "region": os.getenv("S3_REGION_4"),
    },
]

# Initialize S3 clients for each bucket
s3_clients = {
    bucket["name"]: boto3.client(
        "s3",
        aws_access_key_id=bucket["access_key"],
        aws_secret_access_key=bucket["secret_key"],
        region_name=bucket["region"],
    )
    for bucket in buckets
}

def list_objects_in_folder(bucket_name, prefix, continuation_token=None):
    """List objects (folders and files) in the specified prefix with sorting by latest modified files."""
    s3_client = s3_clients[bucket_name]
    
    # Ensure prefix is correctly formatted (Empty string means root)
    params = {"Bucket": bucket_name, "Prefix": prefix, "Delimiter": "/"}
    
    if continuation_token:
        params["ContinuationToken"] = continuation_token

    response = s3_client.list_objects_v2(**params)

    # Extract folders
    folders = [
        {"name": obj.get("Prefix").rstrip("/").split("/")[-1], "path": obj.get("Prefix")}
        for obj in response.get("CommonPrefixes", [])
    ] if "CommonPrefixes" in response else []

    # Extract and sort files by LastModified timestamp (latest first)
    files = sorted(
        [
            {
                "name": obj.get("Key").split("/")[-1],
                "path": obj.get("Key"),
                "last_modified": obj.get("LastModified").isoformat()  # Store timestamp for reference
            }
            for obj in response.get("Contents", []) if obj.get("Key") != prefix
        ],
        key=lambda x: x["last_modified"],  # Sort by LastModified timestamp
        reverse=True  # Latest files first
    ) if "Contents" in response else []

    next_continuation_token = response.get("NextContinuationToken")

    return {
        "folders": folders,
        "files": files,
        "next_continuation_token": next_continuation_token,
    }



@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/list-buckets", methods=["GET"])
def list_buckets():
    """List all available S3 buckets."""
    try:
        bucket_names = [bucket["name"] for bucket in buckets]
        return jsonify({"buckets": bucket_names})
    except Exception as e:
        return str(e), 500

@app.route("/list-files", methods=["GET"])
def list_files():
    """List root folders and files in the selected S3 bucket."""
    try:
        bucket_name = request.args.get("bucket")
        if bucket_name not in s3_clients:
            return "Invalid bucket name", 400

        response = list_objects_in_folder(bucket_name, "")  # Root path
        return jsonify(
            {
                "folders": response["folders"],
                "files": response["files"],
                "next_continuation_token": response["next_continuation_token"],
            }
        )
    except Exception as e:
        return str(e), 500



@app.route("/list-files-in-folder", methods=["GET"])
def list_files_in_folder():
    """List files in a specific folder in the selected S3 bucket."""
    try:
        bucket_name = request.args.get("bucket")
        path = request.args.get("path", "")
        if bucket_name not in s3_clients:
            return "Invalid bucket name", 400

        response = list_objects_in_folder(bucket_name, path)
        return jsonify({"folders": response["folders"], "files": response["files"]})
    except Exception as e:
        return str(e), 500

@app.route("/generate-url/<path:filename>", methods=["GET"])
def generate_url(filename):
    """Generate a pre-signed URL for the given file in the selected bucket."""
    try:
        bucket_name = request.args.get("bucket")
        if bucket_name not in s3_clients:
            return "Invalid bucket name", 400

        s3_client = s3_clients[bucket_name]
        url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": filename}, ExpiresIn=3600
        )  # URL valid for 1 hour
        return jsonify({"url": url})
    except Exception as e:
        return str(e), 500

@app.route("/download", methods=["GET"])
def download():
    """Download a file or zip folder from the selected bucket."""
    bucket_name = request.args.get("bucket")
    path = request.args.get("path", "")
    type = request.args.get("type", "")
    if bucket_name not in s3_clients:
        return "Invalid bucket name", 400

    s3_client = s3_clients[bucket_name]

    if type == "folder":
        # Zip folder
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            paginator = s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name, Prefix=path, Delimiter="/"):
                for obj in page.get("Contents", []):
                    file_key = obj.get("Key")
                    file_name = file_key[len(path):].lstrip("/")
                    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                    zip_file.writestr(file_name, file_obj["Body"].read())
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{path.rstrip('/').split('/')[-1]}.zip",
            mimetype="application/zip",
        )

    elif type == "file":
        try:
            file_obj = s3_client.get_object(Bucket=bucket_name, Key=path)
            return send_file(
                io.BytesIO(file_obj["Body"].read()),
                as_attachment=True,
                download_name=path.split("/")[-1],
                mimetype="application/octet-stream",
            )
        except Exception as e:
            return str(e), 500

@app.route("/upload", methods=["POST"])
def upload():
    """Upload a file to the specified path in the selected S3 bucket."""
    try:
        bucket_name = request.form["bucket"]
        path = request.form["path"]
        file = request.files["file"]

        if bucket_name not in s3_clients:
            return "Invalid bucket name", 400

        s3_client = s3_clients[bucket_name]
        s3_client.upload_fileobj(file, bucket_name, os.path.join(path, file.filename))

        return "File uploaded successfully", 200
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)