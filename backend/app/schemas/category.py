from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = '#3b82f6'
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    weekly_target_hours: float = Field(default=0.0, ge=0)
    max_blocks_per_day: int | None = Field(default=None, ge=1, le=12)
    session_length_minutes: int = Field(default=60, ge=15, le=480)
    min_session_minutes: int = Field(default=30, ge=15, le=300)
    max_session_minutes: int = Field(default=120, ge=15, le=480)
    preferred_days: str | None = None
    preferred_times: str | None = None
    default_location: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = None
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    weekly_target_hours: float | None = Field(default=None, ge=0)
    max_blocks_per_day: int | None = Field(default=None, ge=1, le=12)
    session_length_minutes: int | None = Field(default=None, ge=15, le=480)
    min_session_minutes: int | None = Field(default=None, ge=15, le=300)
    max_session_minutes: int | None = Field(default=None, ge=15, le=480)
    preferred_days: str | None = None
    preferred_times: str | None = None
    default_location: str | None = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
