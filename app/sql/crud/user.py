from typing import Optional

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


async def get_user_by_id(
    user_collection: AsyncIOMotorCollection, id: ObjectId
) -> Optional[dict]:
    user = await user_collection.find_one({"_id": id})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
    return user


async def get_user_by_username(
    user_collection: AsyncIOMotorCollection, username: str
) -> Optional[dict]:
    user = await user_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
    return user


async def get_all_users(
    user_collection: AsyncIOMotorCollection,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_time",
    sort_order: int = 1,
):
    users_cursor = (
        user_collection.find().skip(skip).limit(limit).sort(sort_by, sort_order)
    )
    users = []
    async for user in users_cursor:
        user["id"] = str(user["_id"])
        del user["_id"]
        users.append(user)
    return users


async def get_all_athletes(
    user_collection: AsyncIOMotorCollection,
    sort_by: str = "created_time",
    sort_order: int = 1,
):
    users_cursor = user_collection.find({"role": "athlete"}).sort(sort_by, sort_order)
    users = []
    async for user in users_cursor:
        user["id"] = str(user["_id"])
        del user["_id"]
        users.append(user)
    return users


async def create_user(user_collection: AsyncIOMotorCollection, user_data: dict) -> dict:
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    if new_user:
        new_user["id"] = str(new_user["_id"])
        del new_user["_id"]
    return new_user


async def update_user(
    user_collection: AsyncIOMotorCollection, id: ObjectId, user_data: dict
) -> dict:
    await user_collection.update_one({"_id": id}, {"$set": user_data})
    return await get_user_by_id(user_collection, id)
