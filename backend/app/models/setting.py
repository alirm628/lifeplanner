from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class UserSetting(Base, TimestampMixin):
    __tablename__ = 'user_settings'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True, index=True, nullable=False)

    timezone: Mapped[str] = mapped_column(String(64), default='America/New_York', nullable=False)
    workday_start_hour: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    workday_end_hour: Mapped[int] = mapped_column(Integer, default=22, nullable=False)
    sleep_start_hour: Mapped[int] = mapped_column(Integer, default=23, nullable=False)
    sleep_end_hour: Mapped[int] = mapped_column(Integer, default=7, nullable=False)

    energy_windows: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {
            'high': [{'start': 8, 'end': 12}],
            'medium': [{'start': 12, 'end': 17}],
            'low': [{'start': 17, 'end': 22}],
        },
        nullable=False,
    )

    break_buffer_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    meal_buffer_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    commute_buffer_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    prep_buffer_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    min_gap_between_flexible_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_flexible_minutes_per_day: Mapped[int] = mapped_column(Integer, default=360, nullable=False)
    max_same_category_blocks_per_day: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    user = relationship('User', back_populates='settings')
