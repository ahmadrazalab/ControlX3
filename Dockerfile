# Use official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 5000

# Use environment variables for credentials (to be passed at runtime)
CMD ["python", "app.py"]


# docker run --env-file .env -p 5000:5000 your-dockerhub-username/s3-explorer
