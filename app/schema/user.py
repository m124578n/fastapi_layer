from pydantic import BaseModel

from app.utils.enums import UserPermission


class CreateUser(BaseModel):
    username: str
    password: str
    name: str
    permission: UserPermission


class LoginUser(BaseModel):
    username: str
    password: str


class ChangePassword(BaseModel):
    password: str
    check_password: str
