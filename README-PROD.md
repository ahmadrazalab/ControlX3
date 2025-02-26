### AWS S3 Navigator

## Overview

The **AWS S3 Navigator** is a web-based tool designed to simplify the navigation and management of Amazon S3 buckets. Built with ease of use in mind, this tool allows users to browse, open, upload, and download files within an S3 bucket through a user-friendly web interface. It supports private S3 buckets and utilizes presigned URLs to ensure secure file access.

## Purpose

This tool is designed to provide a straightforward and efficient way to interact with S3 buckets. By offering a web interface, it eliminates the need for complex command-line operations, making it accessible to users who prefer a visual approach to managing their S3 resources.

## Features

- **Browse S3 Buckets**: Navigate through the contents of your S3 bucket with a simple and intuitive interface.
- **File Access**: Open files directly in your browser using presigned URLs, even for private buckets.
- **Search Functionality**: Quickly find specific files or folders within your S3 bucket.
- **File Upload**: Upload files directly to your S3 bucket through the web interface.
- **Download Capability**: Download files and folders from your S3 bucket with ease.
- **Breadcrumb Navigation**: Easily keep track of your current location within the S3 bucket structure.
- **Dynamic Content Display**: View and manage files and folders dynamically based on your navigation.

## Requirements

- **Python 3.x**: Ensure Python is installed on your machine.
- **AWS Access Keys**: Requires AWS access keys with S3 permissions for accessing and managing your S3 bucket.

## Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/ahmadrazalab/AWS-S3-Explorer.git
   ```

2. **Navigate to the Project Folder**

   ```sh
   cd AWS-S3-Explorer
   ```

3. **Set Up a Virtual Environment**

   ```sh
   python3 -m venv venv
   ```

4. **Activate the Virtual Environment**

   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```

5. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

## Run Application

To start the application, use the following command:

```sh
python3 app.py
```

If using the virtual environment, ensure it is activated before running the application.

## Run as a Systemd Service

To run this application as a system service on Linux, follow these steps:

1. **Create a systemd service file**

   ```sh
   sudo nano /etc/systemd/system/aws-s3-navigator.service
   ```

2. **Add the following configuration**

   ```ini
   [Unit]
   Description=AWS S3 Navigator Service
   After=network.target

   [Service]
   User=ubuntu  # Change this to your Linux username
   Group=ubuntu # Change this to your user group
   WorkingDirectory=/path/to/AWS-S3-Explorer
   ExecStart=/path/to/AWS-S3-Explorer/venv/bin/python3 app.py
   Restart=always
   Environment="PATH=/path/to/AWS-S3-Explorer/venv/bin"

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `/path/to/AWS-S3-Explorer` with the actual directory path where the application is located.

3. **Reload systemd and enable the service**

   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable aws-s3-navigator
   sudo systemctl start aws-s3-navigator
   ```

4. **Check service status**

   ```sh
   sudo systemctl status aws-s3-navigator
   ```

## Configuration

Ensure that your AWS access keys and secret keys are properly configured to grant the necessary permissions for accessing your S3 bucket.

## Usage

1. **Select S3 Bucket**

   Choose the desired S3 bucket from the dropdown menu.

2. **Search Files**

   Use the search bar to quickly locate specific files or folders within the bucket.

3. **Navigate Folders**

   Click on folders to browse their contents.

4. **Open Files**

   Click on any file to open it in your browser using a presigned URL with a 1-hour validity.

5. **Upload Files**

   Use the upload option in the header to add files directly to the selected bucket and path.

6. **Download Files**

   Download any file or folder using the provided download button.

## Issues Solved

- **Simple S3 Navigation**: Provides an easy-to-use interface for browsing and managing S3 bucket contents.
- **Secure File Access**: Utilizes presigned URLs to allow secure access to private files.
- **Comprehensive File Management**: Supports file upload, download, and search functionality, making S3 bucket management seamless.

## Contribution

Contributions are welcome! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request to the `main` branch.

## Acknowledgements

Special thanks to all contributors and users who have helped improve this project.

