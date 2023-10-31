from typing import Any

from twilio.base.exceptions import TwilioRestException

from app.server.config import config
from app.server.logger.custom_logger import logger
from app.server.vendor.twilio.client import sms_client


async def send_sms(phone: str, message: str) -> dict[str, Any]:
    """Sends a text message (SMS message) directly to a phone number

    Args:
        phone (str): phone number with country code prefixed
        message (str): message body

    Returns:
        dict[str, Any]: response
    """
    try:
        message_arguments = {'body': message, 'from_': config.TWILIO_NUMBER, 'to': phone}
        sms_client.messages.create(**message_arguments)
        return {'message': 'Successfully sent sms'}
    except TwilioRestException as error:
        logger.exception(f'twilio-sms: {error.code}:{error.status}:{error.msg}')
        return {'message': 'Failed to send sms'}
    except Exception as error:
        logger.exception(f'twilio-sms: {error}')
        return {'message': 'Failed to send sms'}
