import datetime
from datetime import timedelta, timezone


def has_expired(expiry: int) -> bool:
    """
    Checks if the given expiry timestamp has already passed.

    Args:
        expiry (int): The expiry timestamp to check.

    Returns:
        bool: True if the expiry timestamp has already passed, False otherwise.
    """
    return expiry <= get_current_timestamp()


def get_current_timestamp() -> int:
    """
    Returns the current Unix timestamp in milliseconds.

    Returns:
        An integer representing the current Unix timestamp in milliseconds.
    """
    # Get the current timezone-aware datetime object in UTC
    current_time = datetime.datetime.now(timezone.utc)

    # Get the Unix epoch timestamp in seconds
    timestamp_seconds = current_time.timestamp()

    return int(timestamp_seconds * 1000)


def get_timestamp(expires_delta: timedelta = timedelta(hours=1)) -> int:
    """
    Generates a Unix epoch timestamp in milliseconds, given an optional time delta.

    Args:
        expires_delta: A timedelta object representing the time delta to add to the current time. Defaults to 1 hour.

    Returns:
        An integer representing the Unix epoch timestamp in milliseconds.
    """
    # Get the current timezone-aware datetime object in UTC
    current_time = datetime.datetime.now(timezone.utc)
    current_time = current_time + expires_delta

    # Get the Unix epoch timestamp in seconds
    timestamp_seconds = current_time.timestamp()

    return int(timestamp_seconds * 1000)


def get_current_date_time() -> datetime.datetime:
    """
    Returns the current date and time in UTC timezone.

    Returns:
        datetime.datetime: A datetime object representing the current date and time in UTC timezone.
    """
    return datetime.datetime.now(timezone.utc)


def get_n_previous_day_timestamp(days) -> int:
    """
    Returns the UNIX timestamp in milliseconds of `days` number of days ago at midnight UTC.
    Args:
        days (int): The number of days ago to retrieve the timestamp for.
    Returns:
        float: The timestamp in milliseconds.
    """
    prev_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=days)
    midnight_prev_time = datetime.datetime.combine(prev_time, datetime.time.min)
    return int(midnight_prev_time.timestamp() * 1000)


def get_today_midnight_time() -> int:
    """
    Returns the Unix timestamp in milliseconds for midnight of the current day in UTC timezone.
    Returns a float representing the Unix timestamp in milliseconds for midnight of the current day in UTC timezone.
    """
    now = datetime.datetime.now(tz=timezone.utc)
    midnight_date = datetime.datetime(now.year, now.month, now.day, tzinfo=timezone.utc)  # Midnight
    return int(midnight_date.timestamp() * 1000)


def date_to_milliseconds(date_string: str, date_format: str = '%d-%m-%Y') -> int:
    # Create a datetime object from the date string
    date_object = datetime.datetime.strptime(date_string, date_format).replace(tzinfo=timezone.utc)

    # Get the Unix epoch timestamp in seconds
    timestamp_seconds = date_object.timestamp()

    return int(timestamp_seconds * 1000)
