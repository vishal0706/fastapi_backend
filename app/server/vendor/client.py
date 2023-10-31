import aiosmtplib

from app.server.config import config

smtp_client = aiosmtplib.SMTP(hostname=config.SMTP_HOST, port=config.SMTP_PORT, username=config.EMAIL_USERNAME, password=config.EMAIL_PASSWORD)
