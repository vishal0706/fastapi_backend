import os

# Common configuration
PORT = os.environ.get('PORT', 8000)
PROXY_API_PREFIX = os.environ.get('PROXY_API_PREFIX', '')
APP_TITLE = os.environ.get('APP_TITLE', 'FastAPI Backend')
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')

# Oauth JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', os.urandom(32))
LOG_FILE_NAME = os.environ.get('LOG_FILE_NAME', 'app')
# Swagger Doc configuration
DOC_USERNAME = os.environ.get('DOC_USERNAME', 'admin')
DOC_PASSWORD = os.environ.get('DOC_PASSWORD', 'admin')
# Mongo configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/test-dev')
# AWS service configuration
AWS_REGION = os.environ.get('AWS_REGION', 'ap-test')
AWS_ACCESS_ID = os.environ.get('AWS_ACCESS_ID', 'dummy')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'dummy')
AWS_STORAGE_BUCKET = os.environ.get('AWS_STORAGE_BUCKET')
AWS_S3_PRESIGNED_EXPIRATION = int(os.environ.get('AWS_S3_PRESIGNED_EXPIRATION', 60))
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'test@gmail.com')
# SMTP Email client configuration
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
# Azure Service configuration
AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
    'AZURE_STORAGE_CONNECTION_STRING',
    'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;\
        BlobEndpoint=https://test.blob.core.windows.net/;QueueEndpoint=https://test.queue.core.windows.net/;\
            TableEndpoint=https://test.table.core.windows.net/;FileEndpoint=https://test.file.core.windows.net/;',
)
AZURE_PUBLIC_BLOB_CONTAINER_NAME = os.environ.get('AZURE_PUBLIC_BLOB_CONTAINER_NAME', '')
AZURE_PRIVATE_BLOB_CONTAINER_NAME = os.environ.get('AZURE_PRIVATE_BLOB_CONTAINER_NAME', '')
# Twilio
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'test@gmail.com')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'abc123')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'abc123')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER', '123')
