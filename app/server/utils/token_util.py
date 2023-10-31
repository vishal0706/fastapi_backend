import asyncio
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials, HTTPBearer
from jose import jwt

import app.server.database.core_data as core_service
from app.server.config import config
from app.server.static import localization
from app.server.static.collections import Collections
from app.server.static.enums import AccountStatus, TokenType
from app.server.utils import date_utils

security_basic = HTTPBasic()


def authorize_docs(credentials: HTTPBasicCredentials = Depends(security_basic)):
    correct_username = secrets.compare_digest(credentials.username, config.DOC_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, config.DOC_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_USERNAME_PASSWORD_INVALID, headers={'WWW-Authenticate': 'Basic'})
    return credentials.username


def create_jwt_token(payload: dict[str, Any], expires_delta: timedelta = timedelta(days=1), token_type: TokenType = TokenType.BEARER) -> tuple[str, int]:
    """Creates jwt token

    Args:
        payload (dict): json object that needs to be encoded
        expires_delta (Optional[timedelta], optional): token expiry in timedelta. Defaults to timedelta(days=1).

    Returns:
        [str]: encoded jwt token
    """
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    exp_timestamp = int(expire.timestamp() * 1000)
    to_encode.update({'token_type': token_type, 'iat': now, 'exp': expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm='HS256'), exp_timestamp


def verify_jwt_token(token: str, remove_reserved_claims: bool = False) -> dict[str, Any]:
    """Verifies jwt token signature

    Args:
        token (jwt-token): token that needs to be verified

    Returns:
        [JSON]: JSON payload of the decoded token
    """
    decoded_token = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
    if remove_reserved_claims:
        reserved_claims = ['iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti']
        for key in reserved_claims:
            if key in decoded_token:
                del decoded_token[key]
    return decoded_token


async def update_last_active(user_id: int) -> None:
    await core_service.update_one(Collections.USERS, data_filter={'_id': user_id}, update={'$set': {'last_active': date_utils.get_current_timestamp()}})


async def get_current_user(user_data: dict[str, Any], token: str) -> dict[str, Any]:
    pipelines: list[dict[str, Any]] = [
        {'$match': {'user_id': user_data['user_id'], 'user_type': user_data['user_type'], 'access_token': token}},
        {
            '$lookup': {
                'from': Collections.USERS,
                'let': {'user_id': '$user_id', 'user_type': '$user_type'},
                'pipeline': [{'$match': {'$expr': {'$and': [{'$eq': ['$_id', '$$user_id']}, {'$eq': ['$user_type', '$$user_type']}, {'$eq': ['$is_deleted', False]}]}}}],
                'as': 'user',
            }
        },
        {'$unwind': '$user'},
        {'$replaceRoot': {'newRoot': '$user'}},
    ]
    users = await core_service.query_read(Collections.ACCESS_TOKENS, pipelines)
    return users[0] if users else {}


class JWTAuthUser:
    """
    A class used to manage JWT Authentication for a User.

    Attributes:
        security: HTTPBearer scheme for HTTP Authorization.
        access_levels (list): List of access levels the user requires.
        token_type (TokenType): Expected token type for validation.
    """

    # Using HTTP Bearer token security schema
    security = HTTPBearer()

    def __init__(self, access_levels: list[str], token_type: TokenType = TokenType.BEARER):
        """
        The JWTAuthUser constructor.

        Args:
            access_levels (list): List of access levels required by the user.
            token_type (TokenType): Expected token type (defaults to TokenType.BEARER).
        """
        self.access_levels = access_levels
        self.token_type = token_type

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Callable method to verify the authorization token and check the
        user's access levels.

        Args:
            credentials (HTTPAuthorizationCredentials, optional): HTTP authorization
                credentials obtained from the HTTP Bearer token.

        Raises:
            HTTPException: If the token is invalid, user does not exist,
                account is not active, or access level is insufficient.

        Returns:
            dict: The verified token data.
        """
        # Extract the token from the credentials
        token = credentials.credentials

        # Verify the JWT token
        token_data = verify_jwt_token(token.strip())

        # Check if the token type matches the expected token type
        if token_data['token_type'] != self.token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_TOKEN_INVALID)

        # Verify the user
        existing_user = await get_current_user(token_data, token)

        # Check if the user exists
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_TOKEN_INVALID)

        # Check if the user's account is active
        if existing_user['account_status'] != AccountStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=localization.EXCEPTION_ACCOUNT_INACTIVE)

        # Check if the user has the required access level
        if token_data['user_type'] not in self.access_levels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=localization.EXCEPTION_FORBIDDEN_ACCESS)

        # Update the last active time for the user
        asyncio.create_task(update_last_active(token_data['user_id']))

        return token_data
