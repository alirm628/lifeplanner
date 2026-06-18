from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import EventType, LockMode


class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.flexible
    lock_mode: LockMode = LockMode.unlocked
    recurrence_rule: str | None = None
    location: str | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    actual_minutes: int | None = Field(default=None, ge=0)
    category_id: int | None = None

    @model_validator(mode='after')
    def validate_time(self):
        if self.end_time <= self.start_time:
            raise ValueError('end_time must be after start_time')
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    event_type: EventType | None = None
    lock_mode: LockMode | None = None
    recurrence_rule: str | None = None
    location: str | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    actual_minutes: int | None = Field(default=None, ge=0)
    category_id: int | None = None


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class EventDuplicateRequest(BaseModel):
    day_offset: int = 1
