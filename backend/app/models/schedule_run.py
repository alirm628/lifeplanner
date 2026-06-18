from datetime import date
from sqlalchemy import Date, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ScheduleRun(Base, TimestampMixin):
    __tablename__ = 'schedule_runs'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(40), nullable=False)
    proposed_events: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    diagnostics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='generated', nullable=False)
