from datetime import date, datetime
from pydantic import BaseModel

from app.models.enums import EventType, LockMode, ScheduleMode


class ScheduleGenerateRequest(BaseModel):
    week_start: date
    mode: ScheduleMode = ScheduleMode.full_auto


class ProposedEvent(BaseModel):
    title: str
    description: str | None = None
    notes: str | None = None
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.flexible
    lock_mode: LockMode = LockMode.unlocked
    recurrence_rule: str | None = None
    location: str | None = None
    category_id: int | None = None


class CategoryDiagnostic(BaseModel):
    category_id: int
    category_name: str
    target_hours: float
    scheduled_hours: float
    deficit_hours: float
    excess_hours: float
    blocks_scheduled: int


class ScheduleDiagnostics(BaseModel):
    per_category: list[CategoryDiagnostic]
    total_target_hours: float
    total_scheduled_hours: float
    average_daily_flexible_hours: float


class ScheduleGenerateResponse(BaseModel):
    run_id: int
    mode: ScheduleMode
    proposed_events: list[ProposedEvent]
    diagnostics: ScheduleDiagnostics


class ScheduleApplyRequest(BaseModel):
    run_id: int
