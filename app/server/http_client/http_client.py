import httpx
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder


class RestClient:
    def __init__(self, base_url: str = '', timeout: httpx.Timeout = None) -> None:
        self.client = httpx.AsyncClient()
        self.client.base_url = base_url
        self.client.timeout = timeout

    @classmethod
    def init(cls, base_url='', timeout=httpx.Timeout(240.0, connect=10.0)):
        return cls(base_url, timeout)

    async def post(self, end_point: str, params, headers=None):
        try:
            response = await self.client.post(end_point, json=jsonable_encoder(params), headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def post_encoded(self, end_point: str, params, headers=None):
        try:
            response = await self.client.post(end_point, params=params, headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def post_file(self, end_point: str, params=None, files=None, headers=None):
        try:
            response = await self.client.post(end_point, data=jsonable_encoder(params), files=files, headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def get(self, end_point: str, params=None, headers=None):
        try:
            response = await self.client.get(end_point, params=jsonable_encoder(params), headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def patch(self, end_point: str, params=None, headers=None):
        try:
            response = await self.client.patch(end_point, json=jsonable_encoder(params), headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def put(self, end_point: str, params=None, headers=None):
        try:
            response = await self.client.put(end_point, json=jsonable_encoder(params), headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    async def delete(self, end_point: str, params=None, headers=None):
        try:
            response = await self.client.delete(end_point, params=jsonable_encoder(params), headers=headers)
            response = response.json()
            return response
        except httpx.ConnectError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'{error.request.url.port} service unavailable') from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error
