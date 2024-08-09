from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.utils.enums import UserPermission


class UserAuth(BaseModel):
    username: str
    access_token: str


class UserResponseModel(BaseModel):
    id: str
    username: str
    name: Optional[str] = None
    permission: UserPermission
    created_time: datetime


class User(BaseModel):
    id: str
    username: str
    name: str
    permission: UserPermission
    created_time: datetime
