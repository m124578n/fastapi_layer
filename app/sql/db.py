from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from app.config import MONGO_DB, MONGO_URL, REDIS_URL


async def get_database() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    try:
        yield db
    finally:
        client.close()


async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = Redis(connection_pool=ConnectionPool.from_url(REDIS_URL))
    try:
        yield redis
    finally:
        await redis.aclose()
