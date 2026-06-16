# Standard library imports
import os
import logging

# Third-party imports
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
from botocore.exceptions import ClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Environment configuration
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'censo-escolar-bucket')
s3_client = boto3.client('s3')

@app.get("/")
def hello_world():
    return jsonify({"message": "Hello, World!"}), 200

@app.post("/upload")
def upload_file():
    """
    Endpoint to receive a file and upload it to S3.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Faz o upload diretamente do stream para o S3
        s3_client.upload_fileobj(file, S3_BUCKET, file.filename)
        logger.info(f"File {file.filename} uploaded to bucket {S3_BUCKET}")
        return jsonify({"message": f"Arquivo {file.filename} enviado com sucesso!"}), 200
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)