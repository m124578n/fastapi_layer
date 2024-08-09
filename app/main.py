import os
from contextlib import asynccontextmanager

import bcrypt
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import CONTEST_COLLECTION, MONGO_DB, MONGO_URL, USER_COLLECTION
from app.model import user_model
from app.router import auth_router, contest_router, user_router
from app.schema import user_schema
from app.sql.crud import user_crud
from app.sql.db import get_database
from app.utils import create_log


async def startup_db(app: FastAPI):
    create_log("Starting up database")
    app.mongodb_client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb = app.mongodb_client[MONGO_DB]
    contest_collection = app.mongodb[CONTEST_COLLECTION]
    await contest_collection.create_index("name")
    await contest_collection.create_index("athlete.id")
    await contest_collection.create_index("athlete.name")


async def shutdown_db(app: FastAPI):
    create_log("Shutting down database")
    app.mongodb_client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_log("Starting up")
    await startup_db(app)

    yield

    create_log("Shutting down")
    await shutdown_db(app)


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(contest_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.get("/")
def read_root():
    create_log("Hello World")
    return {"message": "Hello World"}


@app.post("/tt/create_user")
async def tt_create_user(
    user: user_schema.CreateUser,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> user_model.UserResponseModel:
    user_collection = db[USER_COLLECTION]
    user_dict = jsonable_encoder(user)
    user_dict["password"] = bcrypt.hashpw(
        user.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    new_user = await user_crud.create_user(user_collection, user_dict)
    new_user = user_model.UserResponseModel(**new_user)
    return new_user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
