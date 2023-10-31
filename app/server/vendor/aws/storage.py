import io
from typing import Any, Union

from botocore.exceptions import ClientError
from fastapi import HTTPException
from fastapi.datastructures import UploadFile

from app.server.config import config
from app.server.utils import file_utils, image_utils
from app.server.vendor.aws.client import storage_client


# pylint: disable=too-many-locals
async def upload_file_with_thumb(folder: str, file: UploadFile, compress: bool = False, quality: int = 90, sizes: list[float] = None) -> dict[str, Any]:
    """Uploads file to specific folder on AWS S3

    Args:
        folder (str): Directory where the file is to be written. Could be nested sub directories
        file (UploadFile): file object

    Returns:
        dict[str, Any]: response
    """
    file_bytes = file.file.read()

    # compress the original image bytes
    if compress:
        file_bytes = image_utils.compress_image_bytes(file_bytes, quality)

    mime_type = file.content_type
    image_type = mime_type.rsplit('/')[0].lower()
    image_data = {}

    if sizes and image_type == 'image':
        resized_images = image_utils.image_to_thumbs_from_bytes(file_bytes, sizes)
        counter = 1
        for size, image_bytes in resized_images.items():
            file_name = f'thumb_{size}_{file.filename}'
            uploaded_res = await upload_file_with_mime_type(folder, image_bytes, file_name, mime_type)
            image_data[f'thumb{counter}'] = uploaded_res
            counter += 1

    original_upload_res = await upload_file_with_mime_type(folder, file_bytes, file.filename, mime_type)
    image_data['original'] = original_upload_res
    return image_data


async def upload_file(folder: str, file: UploadFile) -> dict[str, Any]:
    """Uploads file to specific folder on AWS S3

    Args:
        folder (str): Directory where the file is to be written. Could be nested sub directories
        file (UploadFile): file object

    Returns:
        dict[str, Any]: response
    """
    file_bytes = file.file.read()
    mime_type = file.content_type
    return await upload_file_with_mime_type(folder, file_bytes, file.filename, mime_type)


async def upload_file_with_mime_type(folder: str, file_bytes: Union[io.BytesIO, bytes], file_name: str, mime_type: str) -> dict[str, Any]:
    """Uploads file to specific folder on AWS S3

    Args:
        folder (str): Directory where the file is to be written. Could be nested sub directories
        file_bytes (bytes): file bytes
        file_name (str): original file name
        mime_type (str): file mime type

    Returns:
        dict[str, Any]: response
    """
    filepath = file_utils.get_temp_file_path(folder, file_name, mime_type)
    storage_client.put_object(Key=filepath, Body=file_bytes, Bucket=config.AWS_STORAGE_BUCKET, ContentType=mime_type)
    return {'file_name': file_name, 'mime_type': mime_type, 'key': filepath, 'file': f'https://{config.AWS_STORAGE_BUCKET}.s3.{config.AWS_REGION}.amazonaws.com/{filepath}'}


async def update_presigned_file(*args) -> bool:
    """Update presigned url in the object passed with key as file"""
    for arg in args:
        arg['file'] = await generate_presigned_url(arg['key'])
    return True


async def generate_presigned_url(key: str) -> str:
    method_parameters = {'Bucket': config.AWS_STORAGE_BUCKET, 'Key': key}
    return storage_client.generate_presigned_url(ClientMethod='get_object', Params=method_parameters, ExpiresIn=config.AWS_S3_PRESIGNED_EXPIRATION)


async def generate_presigned_put(key: str = None, acl=None, expires_in=config.AWS_S3_PRESIGNED_EXPIRATION) -> str:
    # content_disposition = f'attachment; filename="{original_file_name}"'
    method_parameters = {'Bucket': config.AWS_STORAGE_BUCKET, 'Key': key}
    if acl:
        method_parameters['ACL'] = acl
    return storage_client.generate_presigned_url(ClientMethod='put_object', Params=method_parameters, ExpiresIn=expires_in)


async def generate_presigned_post(key: str, acl: str = None, content_types: str = None, allowed_size: int = 5e8, expires_in=config.AWS_S3_PRESIGNED_EXPIRATION):
    fields = {}
    conditions = [['starts-with', '$Content-Type', content_type] for content_type in content_types]
    conditions.append(['content-length-range', 1, allowed_size])  # type: ignore[list-item]

    if acl:
        fields['acl'] = acl
        conditions.append({'acl': acl})  # type: ignore[arg-type]

    method_parameters = {'Bucket': config.AWS_STORAGE_BUCKET, 'Key': key, 'ExpiresIn': expires_in, 'Fields': fields, 'Conditions': conditions}
    return storage_client.generate_presigned_post(**method_parameters)


async def get_file_url(file_key: str, presigned_url: bool = False) -> str:
    return await generate_presigned_url(file_key) if presigned_url else f'https://{config.AWS_STORAGE_BUCKET}.s3.{config.AWS_REGION}.amazonaws.com/{file_key}'


async def get_file(file_key: str) -> tuple[Any, Any, Any]:
    """Reads specific file data based on file key

    Args:
        file_key (str): file name

    Returns:
        tuple: file bytes, file name, mimetype
    """
    file_name = file_utils.get_file_name(file_key)
    response = storage_client.get_object(Bucket=config.AWS_STORAGE_BUCKET, Key=file_key)
    return response.get('Body'), file_name, response.get('ContentType')


async def verify_object(key: str, allowed_content_types: list[str] = None):
    try:
        response = storage_client.head_object(Bucket=config.AWS_STORAGE_BUCKET, Key=key)
        content_type = response['ContentType']
        if allowed_content_types and all(allowed_type not in content_type for allowed_type in allowed_content_types):
            raise HTTPException(status_code=400, detail=f'Content type is not valid for file {key}. Allowed content types are {allowed_content_types}')
        return response
    except ClientError as error:
        if error.response['Error']['Code'] == '403':
            raise HTTPException(status_code=404, detail=f'File with name {key} not found') from error
        raise error
