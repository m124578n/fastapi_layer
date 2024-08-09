from datetime import timedelta

import bcrypt
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio.client import Redis

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, USER_COLLECTION
from app.schema import user as schema
from app.sql.crud import user_crud
from app.utils.exception import (
    IncorrectCredentialsException,
    PasswordNotMatchException,
    UserNotFoundException,
)
from app.utils.security import blacklist_token, check_otp, create_access_token


class AuthService:

    @staticmethod
    async def login(
        db: AsyncIOMotorDatabase,
        form_data: schema.LoginUser,
    ):
        user_collection = db.get_collection(USER_COLLECTION)

        data_dict = jsonable_encoder(form_data)
        user_in_db = await user_crud.get_user_by_username(
            user_collection, data_dict["username"]
        )
        if not user_in_db:
            raise IncorrectCredentialsException()

        # 檢查是否使用 OTP 登入
        if user_in_db.get("is_use_otp", False):
            # 檢查 OTP 是否正確
            auth = await check_otp(
                user_collection, ObjectId(user_in_db["id"]), data_dict["password"]
            )
            if not auth:
                raise IncorrectCredentialsException()

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_in_db["username"]}, expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "is_use_otp": True,
            }

        # 檢查密碼是否正確
        if bcrypt.checkpw(
            data_dict["password"].encode("utf-8"),
            user_in_db["password"].encode("utf-8"),
        ):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_in_db["username"]}, expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "is_use_otp": user_in_db.get("is_use_otp", False),
            }
        else:

            raise IncorrectCredentialsException()

    @staticmethod
    async def logout(
        token: str,
        redis: Redis,
    ):
        await blacklist_token(token, redis)
        return {"message": "Logout successful"}

    @staticmethod
    async def change_password(
        db: AsyncIOMotorDatabase,
        current_user: dict,
        form_data: schema.ChangePassword,
    ):
        user_collection = db.get_collection(USER_COLLECTION)

        user_dict = jsonable_encoder(form_data)
        # 檢查密碼是否一致
        if user_dict["check_password"] != user_dict["password"]:
            raise PasswordNotMatchException()

        # 檢查使用者是否存在
        user_in_db = await user_crud.get_user_by_username(
            user_collection, current_user["username"]
        )
        if not user_in_db:
            raise UserNotFoundException()

        user_dict["password"] = bcrypt.hashpw(
            user_dict["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        # 更新密碼
        await user_crud.update_user(
            user_collection,
            ObjectId(user_in_db["id"]),
            {"password": user_dict["password"], "is_use_otp": False},
        )
        return {"message": "successful"}
