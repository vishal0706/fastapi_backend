from typing import Optional

from pydantic import constr

from app.server.models.custom_types import EmailStr
from app.server.models.generic import BaseModel
from app.server.static.enums import AccountStatus, Role


class UserCreateRequest(BaseModel):
    first_name: constr(min_length=1, max_length=150, strip_whitespace=True)
    last_name: constr(min_length=1, max_length=150, strip_whitespace=True)
    email: EmailStr
    country_code: Optional[constr(min_length=1, max_length=5, strip_whitespace=True)] = ''
    phone: Optional[constr(min_length=1, max_length=30, strip_whitespace=True)] = ''


class UserUpdateRequest(BaseModel):
    first_name: Optional[constr(min_length=1, max_length=150, strip_whitespace=True)]
    last_name: Optional[constr(min_length=1, max_length=150, strip_whitespace=True)]
    country_code: Optional[constr(min_length=1, max_length=5, strip_whitespace=True)]
    phone: Optional[constr(min_length=1, max_length=30, strip_whitespace=True)]


class UserCreateDB(BaseModel):
    first_name: str
    last_name: str
    email: str
    country_code: Optional[str] = ''
    phone: Optional[str] = ''
    user_type: Role
    account_status: AccountStatus = AccountStatus.ACTIVE


class UserUpdateDB(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    country_code: Optional[str]
    phone: Optional[str]
    user_type: Role
