from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio.client import Redis

from app.schema import user as schema
from app.service import AuthService
from app.sql.db import get_database, get_redis
from app.utils.enums import all_permissions
from app.utils.exception import (
    IncorrectCredentialsException,
    PasswordNotMatchException,
    UserNotFoundException,
)
from app.utils.security import check_permission

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: schema.LoginUser,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await AuthService.login(db, form_data)
        return res
    except IncorrectCredentialsException:
        raise
    except Exception as e:
        raise e


@router.post("/logout")
async def logout(
    current_user: dict = Depends(check_permission(all_permissions)),
    redis: Redis = Depends(get_redis),
):
    try:
        res = await AuthService.logout(current_user["access_token"], redis)
        return res
    except Exception as e:
        raise e


@router.patch("/password")
async def change_password(
    form_data: schema.ChangePassword,
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await AuthService.change_password(db, current_user, form_data)
        return res
    except PasswordNotMatchException:
        raise
    except UserNotFoundException:
        raise
    except Exception as e:
        raise e
