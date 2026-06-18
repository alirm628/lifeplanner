from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    status: TaskStatus = TaskStatus.todo
    due_date: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    actual_minutes: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    tags: list[str] | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TaskStatus | None = None
    due_date: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    actual_minutes: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    tags: list[str] | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
