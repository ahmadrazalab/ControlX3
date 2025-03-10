# Use official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on (if using Flask's built-in server)
EXPOSE 5000

# Set environment variables (these should be set securely in CI/CD)
ENV S3_BUCKET_1=xxxxxx \
    S3_ACCESS_KEY_1=xxxxxx \
    S3_SECRET_KEY_1=xxxxxx \
    S3_REGION_1=xxxxxx \
    S3_BUCKET_2=xxxxxx \
    S3_ACCESS_KEY_2=xxxxxx \
    S3_SECRET_KEY_2=xxxxxx \
    S3_REGION_2=xxxxxx \
    S3_BUCKET_3=xxxxxx \
    S3_ACCESS_KEY_3=xxxxxx \
    S3_SECRET_KEY_3=xxxxxx \
    S3_REGION_3=xxxxxx \
    S3_BUCKET_4=xxxxxx \
    S3_ACCESS_KEY_4=xxxxxx \
    S3_SECRET_KEY_4=xxxxxx \
    S3_REGION_4=xxxxxx

# Command to run the application
CMD ["python", "app.py"]
