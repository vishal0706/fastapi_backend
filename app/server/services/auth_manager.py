import asyncio
from datetime import timedelta
from typing import Any, Optional

from fastapi import HTTPException, status

import app.server.database.core_data as core_service
from app.server.models.auth import EmailLoginRequest
from app.server.models.custom_types import EmailStr
from app.server.models.passport import PassportTempCreateDB
from app.server.models.users import UserCreateDB, UserCreateRequest
from app.server.static import localization
from app.server.static.collections import Collections
from app.server.static.enums import Role, TokenType
from app.server.utils import crypto_utils, date_utils, password_utils, token_util


async def create_user(params: UserCreateRequest) -> dict[str, Any]:
    """
    Creates a new user.

    Args:
        params (UserCreateRequest): Request body containing User user data.
        org_id (Optional[str]): ID of organization to which the user belongs.

    Returns:
        dict[str, Any]: Dictionary containing the user data.

    Raises:
        HTTPException: If user with the same email already exists.
    """
    user_data = params.dict()

    existing_user = await core_service.read_one(Collections.USERS, data_filter={'email': params.email})
    if existing_user:
        raise HTTPException(status.HTTP_409_CONFLICT, localization.EXCEPTION_EMAIL_IN_USE)

    user_data['user_type'] = Role.TALENT
    password = password_utils.generate_random_password(8)
    encrypted_password = crypto_utils.sha1(password)
    encrypted_password = crypto_utils.sha256(encrypted_password)
    # Running transactions in mongo. Transactions require cluster setup.
    # If any db operation within the content of a transaction fails, the entire transaction is rolled back.
    async with await core_service.get_session() as session:
        async with session.start_transaction():
            user_data = UserCreateDB(**user_data).dict(exclude_none=True)
            create_user_res = await core_service.update_one(Collections.USERS, data_filter={'email': params.email}, update={'$set': user_data}, upsert=True, session=session)
            passport_data = {
                'user_id': create_user_res['_id'],
                'user_type': user_data['user_type'],
                'password': encrypted_password,
                'is_used': False,
                'expiry': date_utils.get_timestamp(expires_delta=timedelta(hours=1)),
            }
            passport_data = PassportTempCreateDB(**passport_data)
            passport_data = passport_data.dict(exclude_none=True)
            await core_service.update_one(Collections.TEMP_PASSPORT, data_filter={'user_id': create_user_res['_id']}, update={'$set': passport_data}, upsert=True, session=session)

    # send email with default password and unique id
    # template = await template_util.get_template(
    #     'app/server/templates/account_details.html', user_name=f'{params.first_name} {params.last_name}', user_id=params.email, password=password, company_name='Wow Labz'
    # )
    # await email_service.send_email([params.email], 'Your Credentials', template, is_html=True)
    return {'message': 'User created successfully'}


async def create_login_token(token_payload: dict[str, Any], user_agent: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Creates a login token and stores it in the database.

    Args:
        token_payload (dict[str, Any]): A dictionary containing the payload for the JWT token.

    Returns:
        dict[str, Any]: A dictionary containing the access and refresh tokens.
    """
    access_token, access_token_expiry = token_util.create_jwt_token(token_payload, timedelta(days=1), token_type=TokenType.BEARER)
    refresh_token, _ = token_util.create_jwt_token(token_payload, timedelta(days=30), token_type=TokenType.REFRESH)
    await core_service.create_one(Collections.ACCESS_TOKENS, {**token_payload, 'access_token': access_token, 'refresh_token': refresh_token, 'metadata': user_agent})
    return {'access_token': access_token, 'access_token_expiry': access_token_expiry, 'refresh_token': refresh_token}


async def refresh_access_token(token: str):
    """
    Refreshes the access token for a user.

    Args:
        token (str): The JWT refresh token.

    Raises:
        HTTPException: If the token is invalid or does not exist in the database.

    Returns:
        dict: A dictionary containing the new access token and its expiry time.
    """
    refresh_token_payload = token_util.verify_jwt_token(token, remove_reserved_claims=True)
    if refresh_token_payload['token_type'] != TokenType.REFRESH:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_REFRESH_TOKEN_INVALID)
    existing_refresh_token = await core_service.read_one(Collections.ACCESS_TOKENS, data_filter={'user_id': refresh_token_payload['user_id'], 'refresh_token': token})
    if not existing_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_REFRESH_TOKEN_INVALID)
    access_token, access_token_expiry = token_util.create_jwt_token(refresh_token_payload, timedelta(days=1))
    del refresh_token_payload['token_type']
    await core_service.create_one(Collections.ACCESS_TOKENS, {**refresh_token_payload, 'access_token': access_token, 'refresh_token': token})
    return {'access_token': access_token, 'access_token_expiry': access_token_expiry}


async def individual_login(params: EmailLoginRequest, user_agent: dict[str, Any]) -> dict[str, Any]:
    """
    Authenticates a user by email and password.

    Args:
        params (EmailLoginRequest): An instance containing the email and password of the user.

    Returns:
        dict: A dictionary containing a JWT token and user information if authentication is successful.

    Raises:
        HTTPException 404: If the user does not exist.
        HTTPException 425: If the user does not have a password or a valid temporary password.
    """

    existing_user = await core_service.read_one(Collections.USERS, data_filter={'email': params.email, 'is_deleted': False})

    if not existing_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, localization.EXCEPTION_USER_NOT_FOUND)

    current_timestamp = date_utils.get_current_timestamp()
    encrypted_password = crypto_utils.sha256(params.password)
    existing_passport = await core_service.read_one(
        Collections.TEMP_PASSPORT, data_filter={'user_id': existing_user['_id'], 'expiry': {'$gte': current_timestamp}, 'is_used': False, 'password': encrypted_password}
    )
    if existing_passport:
        # mark the temp password as used
        await core_service.update_one(Collections.TEMP_PASSPORT, data_filter={'user_id': existing_user['_id']}, update={'$set': {'is_used': True}})

    if not existing_passport:
        existing_passport = await core_service.read_one(Collections.PASSPORT, data_filter={'user_id': existing_user['_id']})
    if not existing_passport:
        raise HTTPException(status.HTTP_425_TOO_EARLY, localization.EXCEPTION_PASSWORD_NOT_FOUND)

    password_utils.check_password(params.password, existing_passport['password'])
    token_payload = {'user_id': existing_user['_id'], 'user_type': existing_user['user_type']}
    token_data = await create_login_token(token_payload, user_agent)
    asyncio.create_task(core_service.update_one(Collections.USERS, data_filter={'_id': existing_user['_id']}, update={'$set': {'last_login': date_utils.get_current_timestamp()}}))
    return {**token_data, 'user_id': existing_user['_id'], 'user_type': existing_user['user_type']}


async def individual_default_password(user_id: str, email: Optional[EmailStr] = None):
    """
    Generates a default password for a given user ID and sends an email with the password.

    Args:
        user_id (str): ID of the user to generate a password for
        email (Optional[EmailStr]): email of the user to send the password to, defaults to None

    Returns:
        dict: a dictionary with a 'message' key indicating that the password was successfully sent

    Raises:
        HTTPException 404 (Not Found): if the user is not found or does not have a registered email
    """
    existing_user = await core_service.read_one(Collections.USERS, data_filter={'_id': user_id, 'user_type': {'$in': [user_type.value for user_type in Role]}})
    if not existing_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, localization.EXCEPTION_USER_NOT_FOUND)
    recipient = email or existing_user['email']
    if not recipient:
        raise HTTPException(status.HTTP_404_NOT_FOUND, localization.EXCEPTION_USER_EMAIL_NOT_REGISTERED)

    # send email
    password = password_utils.generate_random_password(8)
    encrypted_password = crypto_utils.sha1(password)
    encrypted_password = crypto_utils.sha256(encrypted_password)

    passport_data = {
        'user_id': user_id,
        'user_type': existing_user['user_type'],
        'password': encrypted_password,
        'is_used': False,
        'expiry': date_utils.get_timestamp(expires_delta=timedelta(hours=1)),
    }
    passport_data = PassportTempCreateDB(**passport_data)
    passport_data = passport_data.dict(exclude_none=True)
    await core_service.update_one(Collections.TEMP_PASSPORT, data_filter={'user_id': user_id}, update={'$set': passport_data}, upsert=True)
    # template = await template_util.get_template(
    #     'app/server/templates/account_details.html',
    #     user_name=f"{existing_user['first_name']} {existing_user['last_name']}",
    #     user_id=existing_user['email'], password=password, company_name='Wow Labz'
    # )
    # await email_service.send_email([recipient], 'Your Credentials', template, is_html=True)
    return {'message': 'Password successfully sent'}


async def individual_forgot_password(email: EmailStr):
    """
    Sends an email to the user with a randomly generated password and creates a passport token.

    Args:
      email: An email address as a string of the user requesting a new password.

    Returns:
      A dictionary containing the message 'Password successfully sent'.

    Raises:
      HTTPException: If the user is not found in the database.
    """
    existing_user = await core_service.read_one(Collections.USERS, data_filter={'email': email, 'user_type': {'$in': [user_type.value for user_type in Role]}})
    if not existing_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, localization.EXCEPTION_USER_NOT_FOUND)

    password = password_utils.generate_random_password(8)
    encrypted_password = crypto_utils.sha1(password)
    encrypted_password = crypto_utils.sha256(encrypted_password)

    passport_data = {
        'user_id': existing_user['_id'],
        'user_type': existing_user['user_type'],
        'password': encrypted_password,
        'is_used': False,
        'expiry': date_utils.get_timestamp(expires_delta=timedelta(hours=1)),
    }
    passport_data = PassportTempCreateDB(**passport_data)
    passport_data = passport_data.dict(exclude_none=True)
    await core_service.update_one(Collections.TEMP_PASSPORT, data_filter={'user_id': existing_user['_id']}, update={'$set': passport_data}, upsert=True)
    # send email with default password and unique id
    # template = await template_util.get_template(
    #     'app/server/templates/forgot_password.html', user_name=f'{existing_user["first_name"]} {existing_user["last_name"]}', password=password, company_name='Wow Labz'
    # )
    # await email_service.send_email([email], 'Forgot Password', template, is_html=True)
    return {'message': 'Password successfully sent'}


async def get_users_paginated(page: int, page_size: int, search_query: Optional[str]) -> list[dict[str, Any]]:
    """
    Get a paginated list of users.

    Args:
        page (int): The page number to retrieve.
        page_size (int): The number of items to retrieve per page.
        search_query (Optional[str]): A query string to filter the users by name.

    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the users.

    Raises:
        None
    """
    aggregate_query: list[dict[str, Any]] = [{'$match': {'name': {'$regex': search_query, '$options': 'i'}}}, {'$sort': {'name': 1}}] if search_query else [{'$sort': {'name': 1}}]

    return await core_service.query_read(collection_name=Collections.USERS, aggregate=aggregate_query, page=page, page_size=page_size, paging_data=True)
