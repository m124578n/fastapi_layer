from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.model import user as user_model
from app.schema import user as user_schema
from app.service import UserService
from app.sql.db import get_database
from app.utils.enums import all_permissions, high_permissions
from app.utils.exception import (
    IdNotValidException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.utils.security import check_permission

router = APIRouter(prefix="/users", tags=["user"])


@router.get("/me", response_model=user_model.UserResponseModel)
async def get_user(
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        user = await UserService.get_me(db, current_user)
        return user
    except UserNotFoundException:
        raise
    except Exception as e:
        raise e


@router.post("/")
async def create_user(
    user: user_schema.CreateUser,
    current_user: dict = Depends(check_permission(high_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await UserService.create_user(db, user)
        return res
    except UserAlreadyExistsException:
        raise
    except Exception as e:
        raise e


@router.get("/")
async def get_all_users(
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
    sort_by: str = Query("created_time", description="Field to sort by"),
    sort_order: int = Query(
        1, description="Sort order: 1 for ascending, -1 for descending"
    ),
):
    try:
        users = await UserService.get_all_users(
            db=db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return users
    except Exception as e:
        raise e


@router.get("/athletes")
async def get_all_athletes(
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        athletes = await UserService.get_all_athletes(db)
        return athletes
    except Exception as e:
        raise e


@router.get("/{user_id}", response_model=user_model.UserResponseModel)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        user = await UserService.get_user_by_id(db, user_id)
        return user
    except UserNotFoundException:
        raise
    except IdNotValidException:
        raise
    except Exception as e:
        raise e


@router.patch("/{user_id}/reset_password")
async def reset_password(
    user_id: str,
    current_user: dict = Depends(check_permission(high_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await UserService.reset_password(db, user_id, current_user)
        return res
    except IdNotValidException:
        raise
    except UserNotFoundException:
        raise
    except Exception as e:
        raise e
