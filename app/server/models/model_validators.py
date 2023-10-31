from datetime import datetime
from typing import Any

from app.server.models.custom_types import EmailStr

# Generic reusable model validator


def capitalize(value: Any) -> str:
    if isinstance(value, str):
        value = ' '.join((word.capitalize()) for word in value.split(' '))
    elif isinstance(value, list):
        value = [item.capitalize() for item in value]
    return value


def title_case(value: Any) -> str:
    if isinstance(value, str):
        value = ' '.join((word.title()) for word in value.split(' '))
    elif isinstance(value, list):
        value = [item.title() for item in value]
    return value


def upper_case(value: Any) -> str:
    if isinstance(value, str):
        value = ' '.join((word.upper()) for word in value.split(' '))
    elif isinstance(value, list):
        value = [item.upper() for item in value]
    return value


def str_to_list(value: Any):
    if isinstance(value, str):
        value = [item.strip() for item in value.split(',')]
    elif isinstance(value, list):
        if len(value) == 1:
            if value[0] == '':
                value = None
            if value:
                value = [item.strip() for item in value[0].split(',')]

    # Remove duplicates
    if value:
        value = [*set(value)]
    return value


def allow_image_content_type(value: Any):
    if not value:
        return value
    file_type = value.content_type.rsplit('/', 1)[0].lower()
    if value and file_type not in ['image']:
        content_type = value.content_type
        raise ValueError(f'File of type {content_type} not allowed')
    return value


def otp_validate(digits: int):
    def validate(value):
        # Your validation logic here, using custom_value
        if len(str(value)) != digits:
            raise ValueError(f'OTP must be {digits} digits')
        return value

    return validate


def pin_code_validator(digits: int):
    def validate(value):
        # Your validation logic here, using custom_value
        if len(str(value)) < digits:
            raise ValueError(f'Pin code should have {digits} digits')
        return value

    return validate


def email_domain_validator(allowed_domain: str):
    def validate_email_domain(email: EmailStr):
        domain = email.split('@')[-1]
        if domain != allowed_domain:
            raise ValueError(f'Invalid email domain. Allowed domain: {allowed_domain}')
        return email

    return validate_email_domain


def date_format_validator(date_format: str = '%d-%m-%Y', no_past_date: bool = False):
    def validate_date_format(value: str):
        try:
            parsed_date = datetime.strptime(value, date_format).date()
        except ValueError as error:
            raise ValueError(f'Invalid date format. Expected format: {date_format}') from error

        if no_past_date:
            current_date = datetime.now().date()
            if parsed_date < current_date:
                raise ValueError('Date cannot be in the past')
        return value

    return validate_date_format
