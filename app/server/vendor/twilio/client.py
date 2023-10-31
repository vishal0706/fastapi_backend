from sendgrid import SendGridAPIClient
from twilio.rest import Client

from app.server.config import config

sms_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
email_client = SendGridAPIClient(config.SENDGRID_API_KEY)
