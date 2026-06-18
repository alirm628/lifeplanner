from datetime import datetime
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    today_events: list[dict]
    upcoming_events: list[dict]
    weekly_planned_hours: dict[str, float]
    weekly_completed_hours: dict[str, float]
    remaining_free_hours: float
    total_planned_hours: float
    total_completed_hours: float
    generated_at: datetime
