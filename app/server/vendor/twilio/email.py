import base64
import mimetypes
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse

import requests
from pydantic import EmailStr
from sendgrid.helpers.mail import Attachment, Content, Disposition, FileContent, FileName, FileType, Mail

from app.server.config import config
from app.server.logger.custom_logger import logger
from app.server.vendor.twilio.client import email_client


async def process_file(attachment: Union[str, bytes]) -> tuple[str, Optional[str], Optional[str]]:
    """
    Process a file and return its content, file name, and MIME type.

    Args:
        attachment (Union[str, bytes]): The file to be processed. It can be either a file path, a URL, or bytes.

    Returns:
        tuple[str, Optional[str], Optional[str]]: A tuple containing the file content, file name, and MIME type.
            - file_content (str): The content of the file, encoded as base64.
            - file_name (Optional[str]): The name of the file. If the file is bytes or a URL, this will be None.
            - mime_type (Optional[str]): The MIME type of the file. If the MIME type cannot be determined, it will be 'application/octet-stream'.
    """
    if isinstance(attachment, bytes):
        # The file is bytes. Just encode the content.
        file_content = base64.b64encode(attachment).decode()
        # If the file is bytes, we can't determine the file name or MIME type.
        return file_content, None, 'application/octet-stream'

    if attachment.startswith('http://') or attachment.startswith('https://'):
        # The file is a URL. Download the file and get the content.
        response = requests.get(attachment)
        response.raise_for_status()
        file_content = base64.b64encode(response.content).decode()
        file_name = Path(urlparse(attachment).path).name
    else:
        # The file is a file path. Open the file and get the content.
        with Path(attachment).open('rb') as file:
            file_content = base64.b64encode(file.read()).decode()
            file_name = Path(attachment).name

    # Guess the MIME type of the file based on the file name. If it can't be guessed, fallback to 'application/octet-stream'.
    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    return file_content, file_name, mime_type


async def build_email(subject: str, body: str, attachments: list[tuple[Union[str, bytes], Optional[str]]] = None, is_html: bool = False) -> Mail:
    """
    Build an email with the given subject, body, and optional attachments.

    Args:
        subject (str): The subject of the email.
        body (str): The body content of the email.
        attachments (list[tuple[Union[str, bytes], Optional[str]]], optional): A list of attachments to include in the email.
            Each attachment should be a tuple where the first element is the file data and the second element is an optional file name.
            The file data can be a string (representing a file path or URL) or bytes (representing the raw file data). If the file name is not provided,
            and the file data is a string, the name is derived from the file path or URL. Defaults to None.
        is_html (bool, optional): Indicates whether the body content is in HTML format. Defaults to False.

    Returns:
        Mail: The built email message ready to be sent.
    """

    email_params = {'from_email': config.EMAIL_SENDER, 'subject': subject}
    if is_html:
        email_params['plain_text_content'] = Content(mime_type='text/html', content=body)
    else:
        email_params['html_content'] = Content(mime_type='text/plain', content=body)

    message = Mail(**email_params)
    if attachments:
        for file_data, file_name in attachments:
            file_content, actual_file_name, mime_type = await process_file(file_data)
            if file_name is None:
                file_name = actual_file_name

            file_attachment = Attachment(FileContent(file_content), FileName(file_name), FileType(mime_type), Disposition('attachment'))
            message.add_attachment(file_attachment)

    return message


async def send_email(recipients: list[EmailStr], subject: str, body: str, attachments: list[tuple[Union[str, bytes], Optional[str]]] = None, is_html: bool = False) -> dict[str, Any]:
    """
    Send an email to the given recipients with the provided subject and body. Optionally, attach files to the email.

    Args:
        recipients: A list of email addresses to send the email to.
        subject: The subject line of the email.
        body: The body of the email.
        files: A list of tuples where each tuple represents a file to be attached. Each tuple consists of two elements.
               The first element can be a string or bytes. If it's a string, it can be a file path or a URL from where the file will be downloaded.
               If it's bytes, it's the file data directly. The second element in the tuple is an optional string representing the filename.
               If it's None, the actual filename derived from the file path or URL is used. For byte data, if the filename is not provided,
               the default is None and needs to be handled properly.
        is_html: A boolean indicating whether or not the email body is in HTML format. Defaults to False.

    Returns:
        A dictionary with a message indicating whether the email was sent successfully or not.
    """
    try:
        message = await build_email(subject, body, attachments=attachments, is_html=is_html)
        message.add_to(recipients)
        email_client.send(message)
        return {'message': 'Successfully sent email'}
    except Exception as error:
        logger.exception(f'twilio-email: {error}')
        return {'message': 'Failed to send email'}
