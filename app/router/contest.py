from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.model import contest_model
from app.schema import contest_schema
from app.service import ContestService
from app.sql.db import get_database
from app.utils.enums import all_permissions
from app.utils.exception import (
    ContestNotFoundException,
    IdNotValidException,
    UserNotFoundException,
)
from app.utils.security import check_permission

router = APIRouter(prefix="/contests", tags=["contest"])


@router.post("/")
async def create_contest(
    contest: contest_schema.CreateContest,
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await ContestService.create_contest(db, contest, current_user)
        return res
    except UserNotFoundException:
        raise
    except Exception as e:
        raise e


@router.get("/")
async def get_all_contests(
    current_user: dict = Depends(check_permission(all_permissions)),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(10, description="Number of items to retrieve"),
    sort_by: str = Query("created_time", description="Field to sort by"),
    sort_order: int = Query(
        1, description="Sort order: 1 for ascending, -1 for descending"
    ),
    search: str = Query(
        None, description="Search for a contest by name or description"
    ),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await ContestService.get_all_contests(
            db,
            skip,
            limit,
            sort_by,
            sort_order,
            search,
        )
        return res
    except Exception as e:
        raise e


@router.get("/{contest_id}", response_model=contest_model.ContestResponseModel)
async def get_contest_by_id(
    contest_id: str,
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await ContestService.get_contest_by_id(db, contest_id)
        return res
    except ContestNotFoundException:
        raise
    except IdNotValidException:
        raise
    except Exception as e:
        raise e


@router.get(
    "/athletes/{athlete_id}", response_model=list[contest_model.ContestResponseModel]
)
async def get_contest_by_athlete_id(
    athlete_id: str,
    current_user: dict = Depends(check_permission(all_permissions)),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    try:
        res = await ContestService.get_contest_by_athlete_id(db, athlete_id)
        return res
    except Exception as e:
        raise e
