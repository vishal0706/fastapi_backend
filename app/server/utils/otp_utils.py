import math
import random
from datetime import datetime, timedelta, timezone


def generate_otp(expires_delta: timedelta = timedelta(days=1)) -> tuple[str, int]:
    """Generate a one-time password (OTP).
    The generated OTP will expire after a time delta specified by expires_delta.

    Args:
        expires_delta (timedelta, optional): timedelta for the OTP expiration . Defaults to timedelta(days=1).

    Returns:
        tuple[str, int]:: _description_
    """
    # Create a timestamp for the current time
    now = datetime.now(timezone.utc)
    # Add the time delta to the timestamp
    expire = now + expires_delta
    # Create a string of digits
    digits = '0123456789'
    # Create a random number of 6 digits
    otp = ''.join(digits[math.floor(random.random() * 10)] for _ in range(6))
    # @audit hardcoded otp to 123456 for testing
    otp = '123456'
    # Return the random number and the expiration time
    # return ((otp), int(round(expire.timestamp())) * 1000)
    return ((otp), int(round(expire.timestamp())) * 1000)
