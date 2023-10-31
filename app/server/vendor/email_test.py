from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.server.config import config
from app.server.vendor.client import smtp_client


async def send_email(recipient: str, subject: str, body: str, is_html: bool = True) -> dict[str, Any]:
    """
    Asynchronously sends an email to the specified recipient.
    Call this function in background using asyncio.
    `Note:` Using SMTP (Simple Mail Transfer Protocol for sending emails can work for small-scale applications or limited email volumes.
    However, it may not be the most scalable solution for larger applications or high email volumes.
    `It is advised to use this only for testing purposes.`
    Example:
    ```
    asyncio.create_task(send_email('test@example.com', f'Subject', body, is_html=True))
    ```
    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The body of the email.
        is_html (bool, optional): Whether the email body is in HTML format. Defaults to True.
    Returns:
        dict[str, Any]: A dictionary containing information about the sent email.
    """
    message = MIMEMultipart()
    message['From'] = config.EMAIL_SENDER
    message['To'] = recipient
    message['Subject'] = subject
    if is_html:
        email_body = MIMEText(body, 'html', 'utf-8')
    else:
        email_body = MIMEText(body, 'plain', 'utf-8')
    message.attach(email_body)
    await smtp_client.connect()
    email_res = await smtp_client.send_message(message)
    await smtp_client.quit()
    return email_res
