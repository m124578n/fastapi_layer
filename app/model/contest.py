from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.model.user import User
from app.utils.enums import ContestStatus


class Video(BaseModel):
    name: str
    description: str
    url: str
    thumbnail: str
    created_time: datetime


class BaseMetric(BaseModel):
    name: str
    description: str
    unit: str


class TrapMetric(BaseMetric):
    pass


class SkeetMetric(BaseMetric):
    pass


class Contest(BaseModel):
    name: str
    description: Optional[str] = None
    athlete: User
    status: ContestStatus = ContestStatus.INIT
    train_type: str
    metrics: Optional[dict[str, BaseMetric]] = None
    videos: Optional[list[Video]] = None
    created_time: datetime


class ContestResponseModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    athlete: User
    status: ContestStatus
    train_type: str
    metrics: Optional[dict[str, BaseMetric]] = None
    videos: Optional[list[Video]] = None
    created_time: datetime
