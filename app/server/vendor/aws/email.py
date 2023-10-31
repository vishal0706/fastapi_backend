from typing import Any

from app.server.config import config
from app.server.logger.custom_logger import logger
from app.server.vendor.aws.client import email_client


def build_email(subject: str, body: str, is_html: bool = False) -> dict[str, Any]:
    """Builds email message payload

    Args:
        subject (str): email subject
        body (str): email body
        is_html (bool, optional): Flag to identidy whether the message body is in html or plain text format. Defaults to False.

    Returns:
        dict[str, Any]: email message data
    """
    charset = 'UTF-8'
    message = {'Body': {}, 'Subject': {'Charset': charset, 'Data': subject}}
    if is_html:
        message['Body']['Html'] = {'Charset': charset, 'Data': body}
    else:
        message['Body']['Text'] = {'Charset': charset, 'Data': body}

    return message


async def send_email(recipients: list[str], subject: str, body: str, is_html: bool = False) -> dict[str, Any]:
    """Composes an email message and immediately queues it for sending

    Args:
        recipients (list): list of recipients
        subject (str): email subject
        body (str): email body
        is_html (bool, optional): Flag to identify whether the message body is in html or plain text format. Defaults to False.

    Returns:
        dict[str, Any]: email message response
    """
    try:
        response = email_client.send_email(Destination={'ToAddresses': recipients}, Message=build_email(subject, body, is_html=is_html), Source=config.EMAIL_SENDER)
        return {'message': 'Successfully sent email', 'result': response}

    except Exception as error:
        logger.exception(f'aws-email: {error}')
        return {'message': f'Failed to send email: {error}', 'result': {}}
