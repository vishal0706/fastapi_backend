import re
from datetime import datetime, timedelta, timezone

from azure.storage.blob import BlobClient, BlobSasPermissions, ContentSettings, generate_blob_sas
from fastapi import HTTPException, UploadFile

from app.server.config import config
from app.server.utils import file_utils
from app.server.vendor.azure.client import blob_service_client


def is_url(key: str) -> bool:
    """
    Checks if a given string is a URL.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string is a URL, False otherwise.
    """
    url_pattern = re.compile(r'^(http|https|ftp)://')
    return bool(re.match(url_pattern, key))


async def _blob_sas(container_name: str, blob_name: str, expires_delta: timedelta = timedelta(minutes=5), **kwargs) -> str:
    """
    Generates a Shared Access Signature (SAS) token for the given blob in the specified container.

    Args:
        container_name (str): The name of the container.
        blob_name (str): The name of the blob.
        expires_delta (timedelta, optional): The time delta for which the SAS token is valid. Default is 5 minutes.
        **kwargs: Additional arguments that can be passed to BlobSasPermissions.

    Returns:
        str: The generated SAS token for the blob.
    """
    # Set the desired permissions and expiry time for the SAS token
    sas_permissions = BlobSasPermissions(kwargs)  # Adjust permissions as needed
    sas_expiry = datetime.now(timezone.utc) + expires_delta
    return generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=sas_permissions,
        expiry=sas_expiry,
    )


async def get_presigned_download_url(file_key: str, is_private: bool = True, expires_delta: timedelta = timedelta(minutes=5)) -> str:
    """Return a pre-signed URL for downloading a file.

    This async function takes a file key and an optional timedelta object that represents
    the time delta for the pre-signed URL to expire.

    Args:
        file_key: A string representing the key or URL of the file to be downloaded.
        is_private: A boolean indicating whether the file is private or public. Default is True.
        expires_delta: An optional timedelta object representing the expiry time for
            the pre-signed URL. Default is 5 minutes.

    Returns:
        A string representing the pre-signed URL that can be used to download the file.
    """
    # Determine the container name based on whether the file is private or public
    container_name = config.AZURE_PRIVATE_BLOB_CONTAINER_NAME if is_private else config.AZURE_PUBLIC_BLOB_CONTAINER_NAME

    # If the file key is a URL, extract the blob name from it
    if is_url(file_key):
        file_key = BlobClient.from_blob_url(file_key).blob_name

    # Get the blob client for the specified container and file key
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_key)
    if not is_private:
        return blob_client.url
    # Get the shared access signature (SAS) token with read permission and the specified expiry time
    sas_token = await _blob_sas(container_name=container_name, blob_name=file_key, expires_delta=expires_delta, read=True)

    # Construct and return the pre-signed URL by appending the SAS token to the blob URL
    return f'{blob_client.url}?{sas_token}'


async def _upload_file_to_blob_storage(container_name: str, file_bytes: bytes, blob_name: str, content_type: str) -> str:
    """
    Uploads a file to Blob Storage container.
    Args:
        container_name (str): The name of the container.
        file_bytes (bytes): The file bytes to upload.
        blob_name (str): The name of the blob.
        content_type (str): The content type of the blob.
    Returns:
        str: The URL of the uploaded blob.
    """
    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the file to the blob storage
    upload_res = container_client.upload_blob(name=blob_name, data=file_bytes, content_settings=ContentSettings(content_type=content_type), overwrite=True)

    # Return the blob URL
    return upload_res.url


async def upload_file(folder: str, file: UploadFile, is_private: bool = True) -> str:
    """
    Asynchronously uploads a file and returns the path of the uploaded file in blob storage.

    Args:
        folder (str): The folder in which the file will be stored.
        file (UploadFile): The file to be uploaded.
        is_private (bool): Flag indicating whether the file should be stored in a private or public blob container. Default is True.

    Returns:
        str: The path of the uploaded file in blob storage.
    """
    # Determine the container name based on the value of the is_private flag
    container_name = config.AZURE_PRIVATE_BLOB_CONTAINER_NAME if is_private else config.AZURE_PUBLIC_BLOB_CONTAINER_NAME

    # Generate the file path using the folder and filename
    file_path = file_utils.get_temp_file_path(folder=folder, filename=file.filename)

    # Upload the file to blob storage and return the path of the uploaded file
    return await _upload_file_to_blob_storage(container_name=container_name, file_bytes=file.file.read(), blob_name=file_path, content_type=file.content_type)


async def generate_presigned_upload_url(file_key: str, is_private: bool = True, expires_delta: timedelta = timedelta(minutes=10)) -> str:
    """
    Generates a pre-signed URL that can be used to upload a blob to Azure Blob Storage.

    Args:
        file_key (str): The name of the blob to upload.
        is_private (bool, optional): Indicates whether the blob should be uploaded to a private container. Defaults to True.
        expires_delta (timedelta, optional): The time delta for which the SAS token will be valid. Defaults to 10 minutes.

    Returns:
        str: A URL with a time-limited SAS token for uploading the blob.
    """
    # Set the desired expiry time for the SAS token
    sas_permissions = BlobSasPermissions(write=True)  # Adjust permissions as needed
    sas_expiry = datetime.now(timezone.utc) + expires_delta

    # Determine the container name based on the `is_private` flag
    container_name = config.AZURE_PRIVATE_BLOB_CONTAINER_NAME if is_private else config.AZURE_PUBLIC_BLOB_CONTAINER_NAME

    # Get the blob client for the specified container and blob key
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_key)

    # Generate the SAS token for the blob
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=file_key,
        account_key=blob_service_client.credential.account_key,
        permission=sas_permissions,
        expiry=sas_expiry,
    )

    # Return the pre-signed URL with the SAS token
    return f'{blob_client.url}?{sas_token}'


async def verify_blob(file_key: str, allowed_content_types: list[str] = None, is_private: bool = True):
    # Determine the container name based on whether the file is private or public
    container_name = config.AZURE_PRIVATE_BLOB_CONTAINER_NAME if is_private else config.AZURE_PUBLIC_BLOB_CONTAINER_NAME
    blob_client = blob_service_client.get_blob_client(container_name, file_key)

    # Get blob properties
    properties = blob_client.get_blob_properties()
    content_type = properties.content_settings.content_type
    if allowed_content_types and all(allowed_type not in content_type for allowed_type in allowed_content_types):
        raise HTTPException(status_code=400, detail=f'Content type is not valid for file {file_key}. Allowed content types are {allowed_content_types}')
    return properties
