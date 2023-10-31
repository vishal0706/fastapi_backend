from azure.storage.blob import BlobServiceClient

from app.server.config import config

blob_service_client = BlobServiceClient.from_connection_string(config.AZURE_STORAGE_CONNECTION_STRING)
