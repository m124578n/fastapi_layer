from typing import Optional

from pydantic import BaseModel

from app.utils.enums import TrainType


class CreateContest(BaseModel):
    name: str
    athlete_id: str
    train_type: TrainType
    description: Optional[str] = None
