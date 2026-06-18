from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.event import Event
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/summary', response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)
    week_start = today_start - timedelta(days=today_start.weekday())
    week_end = week_start + timedelta(days=7)

    today_events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id, Event.start_time < today_end, Event.end_time > today_start)
        .order_by(Event.start_time.asc())
        .all()
    )

    upcoming_events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id, Event.start_time >= now)
        .order_by(Event.start_time.asc())
        .limit(10)
        .all()
    )

    week_events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id, Event.start_time < week_end, Event.end_time > week_start)
        .all()
    )

    categories = {c.id: c.name for c in db.query(Category).filter(Category.user_id == current_user.id).all()}

    weekly_planned: dict[str, float] = {}
    weekly_completed: dict[str, float] = {}
    total_planned = 0.0
    total_completed = 0.0

    for event in week_events:
        hours = max(0.0, (event.end_time - event.start_time).total_seconds() / 3600)
        name = categories.get(event.category_id, 'Uncategorized')
        weekly_planned[name] = round(weekly_planned.get(name, 0.0) + hours, 2)
        total_planned += hours

        actual_hours = (event.actual_minutes or 0) / 60
        weekly_completed[name] = round(weekly_completed.get(name, 0.0) + actual_hours, 2)
        total_completed += actual_hours

    total_week_hours = 7 * 24
    remaining_free = max(0.0, total_week_hours - total_planned)

    return DashboardSummary(
        today_events=[
            {
                'id': e.id,
                'title': e.title,
                'start_time': e.start_time.isoformat(),
                'end_time': e.end_time.isoformat(),
                'event_type': e.event_type.value,
                'lock_mode': e.lock_mode.value,
            }
            for e in today_events
        ],
        upcoming_events=[
            {
                'id': e.id,
                'title': e.title,
                'start_time': e.start_time.isoformat(),
                'end_time': e.end_time.isoformat(),
                'event_type': e.event_type.value,
                'lock_mode': e.lock_mode.value,
            }
            for e in upcoming_events
        ],
        weekly_planned_hours=weekly_planned,
        weekly_completed_hours=weekly_completed,
        remaining_free_hours=round(remaining_free, 2),
        total_planned_hours=round(total_planned, 2),
        total_completed_hours=round(total_completed, 2),
        generated_at=now,
    )
