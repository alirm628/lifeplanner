from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SettingBase(BaseModel):
    timezone: str = 'America/New_York'
    workday_start_hour: int = Field(default=8, ge=0, le=23)
    workday_end_hour: int = Field(default=22, ge=1, le=24)
    sleep_start_hour: int = Field(default=23, ge=0, le=23)
    sleep_end_hour: int = Field(default=7, ge=0, le=23)
    energy_windows: dict = {
        'high': [{'start': 8, 'end': 12}],
        'medium': [{'start': 12, 'end': 17}],
        'low': [{'start': 17, 'end': 22}],
    }
    break_buffer_minutes: int = Field(default=10, ge=0, le=120)
    meal_buffer_minutes: int = Field(default=30, ge=0, le=180)
    commute_buffer_minutes: int = Field(default=15, ge=0, le=180)
    prep_buffer_minutes: int = Field(default=10, ge=0, le=120)

    min_gap_between_flexible_minutes: int = Field(default=30, ge=0, le=180)
    max_flexible_minutes_per_day: int = Field(default=360, ge=60, le=900)
    max_same_category_blocks_per_day: int = Field(default=2, ge=1, le=10)


class SettingUpdate(BaseModel):
    timezone: str | None = None
    workday_start_hour: int | None = Field(default=None, ge=0, le=23)
    workday_end_hour: int | None = Field(default=None, ge=1, le=24)
    sleep_start_hour: int | None = Field(default=None, ge=0, le=23)
    sleep_end_hour: int | None = Field(default=None, ge=0, le=23)
    energy_windows: dict | None = None
    break_buffer_minutes: int | None = Field(default=None, ge=0, le=120)
    meal_buffer_minutes: int | None = Field(default=None, ge=0, le=180)
    commute_buffer_minutes: int | None = Field(default=None, ge=0, le=180)
    prep_buffer_minutes: int | None = Field(default=None, ge=0, le=120)
    min_gap_between_flexible_minutes: int | None = Field(default=None, ge=0, le=180)
    max_flexible_minutes_per_day: int | None = Field(default=None, ge=60, le=900)
    max_same_category_blocks_per_day: int | None = Field(default=None, ge=1, le=10)


class SettingRead(SettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
