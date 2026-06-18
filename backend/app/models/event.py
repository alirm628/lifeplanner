from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EventType, LockMode
from app.models.mixins import TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    event_type: Mapped[EventType] = mapped_column(Enum(EventType), default=EventType.flexible, nullable=False)
    lock_mode: Mapped[LockMode] = mapped_column(Enum(LockMode), default=LockMode.unlocked, nullable=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user = relationship('User', back_populates='events')
    category = relationship('Category', back_populates='events')
