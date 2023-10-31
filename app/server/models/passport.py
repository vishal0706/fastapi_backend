from typing import Optional

from app.server.models.custom_types import EmailStr
from app.server.models.generic import BaseModel
from app.server.static.enums import Role


class PassportCreateDB(BaseModel):
    user_id: str
    password: str
    user_type: Role


class PassportTempCreateDB(BaseModel):
    user_id: str
    password: str
    user_type: Role
    is_used: bool = False
    expiry: int


class SendPasswordRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None


class ForgotPasswordOrgRequest(BaseModel):
    email: EmailStr
    org_id: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
