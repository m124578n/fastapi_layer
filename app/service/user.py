import bcrypt
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import USER_COLLECTION
from app.model import user_model
from app.schema import user_schema
from app.sql.crud import user_crud
from app.utils import create_log
from app.utils.exception import (
    IdNotValidException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.utils.security import create_one_time_password, get_now


class UserService:

    @staticmethod
    async def get_me(db: AsyncIOMotorDatabase, current_user: dict):
        user_collection = db.get_collection(USER_COLLECTION)
        user = await user_crud.get_user_by_id(
            user_collection, ObjectId(current_user["id"])
        )
        if not user:
            raise UserNotFoundException()
        return user

    @staticmethod
    async def create_user(
        db: AsyncIOMotorDatabase,
        user: user_schema.CreateUser,
    ):
        user_collection = db.get_collection(USER_COLLECTION)
        user_dict = jsonable_encoder(user)
        user = await user_crud.get_user_by_username(
            user_collection, user_dict["username"]
        )
        if user:
            raise UserAlreadyExistsException()

        user_dict["password"] = bcrypt.hashpw(
            user_dict["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user_dict["created_time"] = get_now()
        new_user = await user_crud.create_user(user_collection, user_dict)
        new_user = user_model.UserResponseModel(**new_user)
        return new_user

    @staticmethod
    async def get_all_users(
        db: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_time",
        sort_order: int = 1,
    ):
        user_collection = db.get_collection(USER_COLLECTION)
        users = await user_crud.get_all_users(
            user_collection,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return users

    @staticmethod
    async def get_all_athletes(db: AsyncIOMotorDatabase):
        user_collection = db.get_collection(USER_COLLECTION)
        users = await user_crud.get_all_athletes(user_collection)
        return users

    @staticmethod
    async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str):
        try:
            user_id = ObjectId(user_id)
        except:
            raise IdNotValidException()
        user_collection = db.get_collection(USER_COLLECTION)
        user = await user_crud.get_user_by_id(user_collection, user_id)
        if not user:
            raise UserNotFoundException()
        return user

    @staticmethod
    async def reset_password(
        db: AsyncIOMotorDatabase, user_id: str, current_user: dict
    ):
        user_collection = db.get_collection(USER_COLLECTION)
        try:
            user_id = ObjectId(user_id)
        except:
            raise IdNotValidException()
        # 檢查使用者是否存在
        user_in_db = await user_crud.get_user_by_id(user_collection, user_id)
        if not user_in_db:
            raise UserNotFoundException()

        # 產生 OTP
        otp = create_one_time_password(user_in_db["id"])

        # 將 OTP 加密
        bcrypt_password = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        # 更新使用 OTP 登入的狀態
        await user_crud.update_user(
            user_collection,
            ObjectId(user_in_db["id"]),
            {"is_use_otp": True, "password": bcrypt_password},
        )
        create_log(
            f"user {current_user['username']} reset password for user {user_in_db['username']}"
        )
        return {"message": "successful", "otp": otp}
