import asyncio
import contextlib

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import app.server.database.core_data as core_service
from app.server.logger.custom_logger import logger
from app.server.static.collections import Collections
from app.server.utils import token_util


class RequestsTrackerMiddleware(BaseHTTPMiddleware):
    """Request tracker middleware to log IP addresses for each requests along with user id if the request as Authorization header"""

    async def dispatch(self, request: Request, call_next):
        asyncio.create_task(tract_request_address(request))
        response = await call_next(request)
        asyncio.create_task(logging_api_requests(request, response))
        return response


async def logging_api_requests(request: Request, response: Response):
    if forwarded := request.headers.get('X-Forwarded-For'):
        host = forwarded.split(',')[0]
    else:
        host = request.client.host
    request_headers = dict(request.headers)
    response_headers = dict(response.headers)
    logger_ctx = logger.bind(client_ip=host, url=request.url, method=request.method, status=response.status_code, request_headers=request_headers, response_headers=response_headers)
    logger_ctx.debug('Request received')


async def tract_request_address(request: Request):
    host = ''
    user_id = ''
    # extract user id from authorization header of the request
    if 'authorization' in request.headers:
        token = request.headers.get('authorization')
        parts = token.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer' and parts[1] not in ['', ' ', 'null']:
            token = token.split(' ')[-1]
            with contextlib.suppress(Exception):
                if user := token_util.verify_jwt_token(token):
                    user_id = user['user_id']
    if forwarded := request.headers.get('X-Forwarded-For'):
        host = forwarded.split(',')[0]
    else:
        host = request.client.host

    data = {'user_id': user_id, 'ip': host, 'path': f"{request.scope['method']}:{request.scope['path']}"}
    await core_service.update_one(Collections.REQUEST_TRACKER, data_filter=data, update={'$inc': {'count': 1}}, upsert=True)
