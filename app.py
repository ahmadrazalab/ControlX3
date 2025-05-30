import boto3
import io
import zipfile
from flask import Flask, jsonify, request, send_file, render_template
from dotenv import load_dotenv
import os
import sqlite3
import bcrypt
from flask import Flask, jsonify, request, send_file, session, redirect, url_for, render_template_string
from botocore.client import Config
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Set a secret key for session management



# Load environment variables from .env file
load_dotenv()


# login prmpt 
# Add this function to handle authentication
def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password,id FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return {"status":True,"user_id":result[1]}
    return {"status":False,"user_id":None}

def add_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         res=check_user(username, password)
#         if res["status"]:
#             session["logged_in"] = True
#             session["user_id"] = res["user_id"]
#             return redirect(url_for("index"))
#         else:
#             return "Invalid credentials", 401
#     return render_template_string('''
#         <form method="post">
#             Username: <input type="text" name="username"><br>
#             Password: <input type="password" name="password"><br>
#             <input type="submit" value="Login">
#         </form>
#     ''')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        res = check_user(username, password)
        if res["status"]:
            session["logged_in"] = True
            session["user_id"] = res["user_id"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

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
        "by_admin_only": os.getenv("S3_BUCKET_1_BY_ADMIN_ONLY"),
    },
    {
        "name": os.getenv("S3_BUCKET_2"),
        "access_key": os.getenv("S3_ACCESS_KEY_2"),
        "secret_key": os.getenv("S3_SECRET_KEY_2"),
        "region": os.getenv("S3_REGION_2"),
        "by_admin_only": os.getenv("S3_BUCKET_2_BY_ADMIN_ONLY"),

    },
    {
        "name": os.getenv("S3_BUCKET_3"),
        "access_key": os.getenv("S3_ACCESS_KEY_3"),
        "secret_key": os.getenv("S3_SECRET_KEY_3"),
        "region": os.getenv("S3_REGION_3"),
        "by_admin_only": os.getenv("S3_BUCKET_3_BY_ADMIN_ONLY"),


    },
    {
        "name": os.getenv("S3_BUCKET_4"),
        "access_key": os.getenv("S3_ACCESS_KEY_4"),
        "secret_key": os.getenv("S3_SECRET_KEY_4"),
        "region": os.getenv("S3_REGION_4"),
        "by_admin_only": os.getenv("S3_BUCKET_4_BY_ADMIN_ONLY"),
    },
]

r2Buckets=[{
        "name": os.getenv("R2_BUCKET_NAME_1"),
        "endpoint_url": os.getenv("R2_ENDPOINT_URL_1"),
        "aws_access_key_id": os.getenv("R2_ACCESS_KEY_ID_1"),
        "aws_secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY_1"),
        "by_admin_only": os.getenv("R2_BUCKET_1_BY_ADMIN_ONLY"),
        "token": os.getenv("R2_ACCESS_TOKEN_1")
},
{
        "name": os.getenv("R2_BUCKET_NAME_2"),
        "endpoint_url": os.getenv("R2_ENDPOINT_URL_2"),
        "aws_access_key_id": os.getenv("R2_ACCESS_KEY_ID_2"),
        "aws_secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY_2"),
        "by_admin_only": os.getenv("R2_BUCKET_2_BY_ADMIN_ONLY"),
        "token": os.getenv("R2_ACCESS_TOKEN_2")
},
{
        "name": os.getenv("R2_BUCKET_NAME_3"),
        "endpoint_url": os.getenv("R2_ENDPOINT_URL_3"),
        "aws_access_key_id": os.getenv("R2_ACCESS_KEY_ID_3"),
        "aws_secret_access_key": os.getenv("R2_SECRET_ACCESS_KEY_3"),
        "by_admin_only": os.getenv("R2_BUCKET_3_BY_ADMIN_ONLY"),
        "token": os.getenv("R2_ACCESS_TOKEN_3")
}
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
for r2bucket in r2Buckets:
    s3_clients[r2bucket["name"]] = boto3.client(
    "s3",
    endpoint_url=os.getenv('R2_ENDPOINT_URL_1'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID_1'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY_1'),
    config=Config(signature_version="s3v4"),  
    )
def get_token_by_name(bucket_name):
    """Return the token for a given R2 bucket name"""
    for bucket in r2Buckets:
        if bucket["name"] == bucket_name:
            return bucket["token"]
    return None  

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
        key=lambda x: x["last_modified"],  
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
        user_id  = session.get("user_id", None) 
        print(user_id)

        bucket_names = [bucket["name"] for bucket in buckets if (user_id!=1 and bucket["by_admin_only"] != "true") or (user_id==1 and bucket["by_admin_only"] in ["false", "true"]) ]
        
        r2_bucket_names = [bucket["name"] for bucket in r2Buckets if (user_id!=1 and bucket["by_admin_only"] != "true") or (user_id==1 and bucket["by_admin_only"] in ["false", "true"]) ]
        bucket_names.extend(r2_bucket_names)

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
        
        token =None
        if bucket_name in r2Buckets:
            token = get_token_by_name(bucket_name)
            

        response = list_objects_in_folder(bucket_name, "",token)  
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
