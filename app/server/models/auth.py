from pydantic import constr

from app.server.models.custom_types import EmailStr
from app.server.models.generic import BaseModel


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=4, max_length=100, strip_whitespace=True)


class OrganizationLoginRequest(BaseModel):
    unique_id: str
    password: constr(min_length=4, max_length=100, strip_whitespace=True)
