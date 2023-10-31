from typing import Any, Optional

from fastapi import APIRouter, Body, Depends

from app.server.middlewares.headers import get_user_agent
from app.server.models.auth import EmailLoginRequest
from app.server.models.passport import ForgotPasswordRequest, SendPasswordRequest
from app.server.models.users import UserCreateRequest
from app.server.services import auth_manager
from app.server.static.enums import Role
from app.server.utils.token_util import JWTAuthUser

router = APIRouter()


@router.post('/users/create', summary='Creates new users')
async def create_user(params: UserCreateRequest) -> dict[str, Any]:
    data = await auth_manager.create_user(params)
    return {'data': data, 'status': 'SUCCESS'}


@router.post('/auth/refresh', summary='Creates new access token for session maintenance')
async def refresh_access_token(refresh_token: str = Body(..., embed=True)) -> dict[str, Any]:
    data = await auth_manager.refresh_access_token(refresh_token)
    return {'data': data, 'status': 'SUCCESS'}


@router.post('/auth/users/login', summary='Email based login')
async def individual_login(params: EmailLoginRequest, user_agent: dict[str, Any] = Depends(get_user_agent)) -> dict[str, Any]:
    data = await auth_manager.individual_login(params, user_agent)
    return {'data': data, 'status': 'SUCCESS'}


@router.post('/auth/users/password/send', summary='Creates a new default password and sends it to the user on registered email')
async def individual_default_password(params: SendPasswordRequest, _token=Depends(JWTAuthUser([Role.SUPER_ADMIN]))) -> dict[str, Any]:
    data = await auth_manager.individual_default_password(params.user_id, email=params.email)
    return {'data': data, 'status': 'SUCCESS'}


@router.post('/auth/users/password/forgot', summary='Creates a new default password and sends it to the user on registered email')
async def individual_forgot_password(params: ForgotPasswordRequest) -> dict[str, Any]:
    data = await auth_manager.individual_forgot_password(params.email)
    return {'data': data, 'status': 'SUCCESS'}


@router.get('/auth/users/paginated', summary='Gets all users in paginated form')
async def get_all_industry_paginated(page: int = 1, page_size: int = 10, search_query: Optional[str] = None) -> dict[str, Any]:
    data = await auth_manager.get_users_paginated(page=page, page_size=page_size, search_query=search_query)
    return {'data': data, 'status': 'SUCCESS'}
