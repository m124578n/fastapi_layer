import bcrypt
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from app.config import REDIS_URL, USER_COLLECTION
from app.main import app
from app.sql.db import get_database, get_redis
from tests.config import MONGO_DB, MONGO_URL


@pytest_asyncio.fixture(scope="session")
async def test_client(init_db_data):
    app.dependency_overrides[get_database] = lambda: AsyncIOMotorDatabase(
        AsyncIOMotorClient(MONGO_URL), MONGO_DB
    )
    app.dependency_overrides[get_redis] = lambda: Redis(
        connection_pool=ConnectionPool.from_url(REDIS_URL)
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def test_db() -> AsyncIOMotorDatabase:
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client[MONGO_DB]
    yield db
    # await client.drop_database(MONGO_DB)


@pytest_asyncio.fixture(scope="session")
async def test_redis() -> Redis:
    redis = Redis(connection_pool=ConnectionPool.from_url(REDIS_URL))
    yield redis
    # await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture(scope="session")
async def init_db_data(test_db, test_redis):
    # 初始化數據庫資料
    password = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    test_user = {
        "username": "testuser",
        "password": hashed_password,
        "permission": "athlete",
        "is_use_otp": False,
    }
    await test_db[USER_COLLECTION].insert_one(test_user)
    yield
    await test_db[USER_COLLECTION].delete_many({})
