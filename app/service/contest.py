from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import CONTEST_COLLECTION, USER_COLLECTION
from app.model import contest_model, user_model
from app.schema import contest_schema
from app.sql.crud import contest_crud, user_crud
from app.utils.enums import ContestStatus
from app.utils.exception import (
    ContestNotFoundException,
    IdNotValidException,
    UserNotFoundException,
)
from app.utils.security import get_now


class ContestService:

    @staticmethod
    async def create_contest(
        db: AsyncIOMotorDatabase,
        contest: contest_schema.CreateContest,
        current_user: dict,
    ):
        contest_collection = db.get_collection(CONTEST_COLLECTION)
        user_collection = db.get_collection(USER_COLLECTION)

        contest_dict = jsonable_encoder(contest)

        # check if the athlete is in the database
        athlete = await user_crud.get_user_by_id(
            user_collection, contest_dict["athlete_id"]
        )
        if not athlete:
            raise UserNotFoundException()

        athlete = user_model.User(**athlete)
        new_contest = contest_model.Contest(
            name=contest_dict["name"],
            description=contest_dict["description"],
            train_type=contest_dict["train_type"],
            athlete=athlete,
            status=ContestStatus.INIT,
            videos=None,
            metrics=None,
            created_time=get_now(),
        ).model_dump()

        new_contest = await contest_crud.create_contest(contest_collection, new_contest)
        new_contest = contest_model.ContestResponseModel(**new_contest)
        return new_contest

    @staticmethod
    async def get_all_contests(
        db: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_time",
        sort_order: int = 1,
        search: str = None,
    ):
        contest_collection = db.get_collection(CONTEST_COLLECTION)
        contests = await contest_crud.get_all_contests(
            contest_collection,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        return contests

    @staticmethod
    async def get_contest_by_id(db: AsyncIOMotorDatabase, contest_id: str):
        contest_collection = db.get_collection(CONTEST_COLLECTION)
        try:
            contest_id = ObjectId(contest_id)
        except:
            raise IdNotValidException()
        contest_in_db = await contest_crud.get_contest_by_id(
            contest_collection, contest_id
        )
        if not contest_in_db:
            raise ContestNotFoundException()
        return contest_in_db

    @staticmethod
    async def get_contest_by_athlete_id(db: AsyncIOMotorDatabase, athlete_id: str):
        contest_collection = db.get_collection(CONTEST_COLLECTION)
        contests = await contest_crud.get_contest_by_athlete_id(
            contest_collection, athlete_id
        )
        return contests
