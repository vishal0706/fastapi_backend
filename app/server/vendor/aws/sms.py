from typing import Any

from app.server.logger.custom_logger import logger
from app.server.vendor.aws.client import sms_client


async def send_sms(phone: str, message: str) -> dict[str, Any]:
    """Sends a text message (SMS message) directly to a phone number

    Args:
        phone (str): phone number with country code prefixed
        message (str): message body

    Returns:
        dict[str, Any]: response
    """
    try:
        response = sms_client.publish(PhoneNumber=phone, Message=message, MessageAttributes={'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}})
        return {'message': 'Successfully sent sms', 'result': response}
    except Exception as error:
        logger.exception(f'aws-sms: {error}')
        return {'message': 'Failed to sent sms', 'result': {}}
