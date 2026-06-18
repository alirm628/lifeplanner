from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default='#3b82f6', nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    weekly_target_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_blocks_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_length_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    min_session_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_session_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    preferred_days: Mapped[str | None] = mapped_column(String(64), nullable=True)
    preferred_times: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship('User', back_populates='categories')
    events = relationship('Event', back_populates='category')
