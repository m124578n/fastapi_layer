from datetime import timedelta

import bcrypt
import jwt
from redis.asyncio.client import Redis
from bson.objectid import ObjectId
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    USER_COLLECTION,
)
from app.sql.crud import user_crud
from app.sql.db import get_database, get_redis
from app.utils import get_now
from app.utils.enums import UserPermission
from app.utils.exception import CredentialsException, ForbiddenException

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = get_now() + expires_delta
    else:
        expire = get_now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_one_time_password(username: str, length: int = 8):
    import hashlib
    import random
    import string

    # 使用用户名生成一个哈希值
    hash_object = hashlib.sha256(username.encode())
    hash_hex = hash_object.hexdigest()

    # 使用哈希值作为随机数生成器的种子
    random.seed(hash_hex)

    # 生成一个八位数的随机码
    random_code = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )
    return random_code


async def check_otp(
    user_collection: AsyncIOMotorCollection,
    user_id: ObjectId,
    password: str,
):
    user = await user_crud.get_user_by_id(user_collection, user_id)
    if user["is_use_otp"] and bcrypt.checkpw(
        password.encode("utf-8"), user["password"].encode("utf-8")
    ):
        return user
    return None


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security_scheme),
    redis: Redis = Depends(get_redis),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_collection = db[USER_COLLECTION]

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException()
    except jwt.PyJWTError:
        raise CredentialsException()

    # Check if token is blacklisted
    is_blacklisted = await redis.get(f"blacklist_{token.credentials}")
    if is_blacklisted:
        raise CredentialsException()

    user = await user_crud.get_user_by_username(user_collection, username)
    if user is None:
        raise CredentialsException()
    user["access_token"] = token.credentials
    return user


def check_permission(user_permission: list[UserPermission]):
    def _check_permission(current_user: dict = Depends(get_current_user)):
        if current_user.get("permission", None) not in user_permission:
            raise ForbiddenException()
        return current_user

    return _check_permission


async def blacklist_token(token: str, redis: Redis):
    await redis.set(f"blacklist_{token}", "true", ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
