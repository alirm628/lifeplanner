from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    planned_hours: float
    completed_hours: float
    missed_hours: float
    consistency_score: float
    productivity_score: float


class CategoryBreakdownItem(BaseModel):
    category: str
    planned_hours: float
    completed_hours: float


class TrendPoint(BaseModel):
    label: str
    planned_hours: float
    completed_hours: float


class HeatmapPoint(BaseModel):
    weekday: int
    hour: int
    count: int
