from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import GoalStatus


class GoalBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category_id: int | None = None
    target_hours: float | None = Field(default=None, ge=0)
    target_sessions: int | None = Field(default=None, ge=0)
    target_date: date | None = None
    status: GoalStatus = GoalStatus.active


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_id: int | None = None
    target_hours: float | None = Field(default=None, ge=0)
    target_sessions: int | None = Field(default=None, ge=0)
    target_date: date | None = None
    status: GoalStatus | None = None


class GoalRead(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class GoalProgress(BaseModel):
    goal_id: int
    title: str
    status: GoalStatus
    progress_hours: float
    progress_sessions: int
    target_hours: float | None
    target_sessions: int | None
