import re

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


async def get_contest_by_id(contest_collection: AsyncIOMotorCollection, id: ObjectId):
    contest = await contest_collection.find_one({"_id": id})
    if contest:
        contest["id"] = str(contest["_id"])
        del contest["_id"]
    return contest


async def get_contest_by_athlete_id(
    contest_collection: AsyncIOMotorCollection, athlete_id: str
):
    contests_cursor = contest_collection.find({"athlete.id": athlete_id})
    contests = []
    async for contest in contests_cursor:
        contest["id"] = str(contest["_id"])
        del contest["_id"]
        contests.append(contest)
    return contests


async def get_all_contests(
    contest_collection: AsyncIOMotorCollection,
    search: str = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_time",
    sort_order: int = 1,
):
    query = {}
    if search:
        # 转义特殊字符并使搜索大小写不敏感
        escaped_search = re.escape(search)
        regex_pattern = {"$regex": f".*{escaped_search}.*", "$options": "i"}
        query = {"$or": [{"name": regex_pattern}, {"athlete.name": regex_pattern}]}

    contests_cursor = (
        contest_collection.find(query).skip(skip).limit(limit).sort(sort_by, sort_order)
    )
    contests = []
    async for contest in contests_cursor:
        contest["id"] = str(contest["_id"])
        del contest["_id"]
        contests.append(contest)
    return contests


async def create_contest(
    contest_collection: AsyncIOMotorCollection, contest_data: dict
):
    contest = await contest_collection.insert_one(contest_data)
    new_contest = await contest_collection.find_one({"_id": contest.inserted_id})
    if new_contest:
        new_contest["id"] = str(new_contest["_id"])
        del new_contest["_id"]
    return new_contest


async def update_contest(
    contest_collection: AsyncIOMotorCollection, id: ObjectId, contest_data: dict
):
    await contest_collection.update_one({"_id": id}, {"$set": contest_data})
    return await get_contest_by_id(contest_collection, id)
