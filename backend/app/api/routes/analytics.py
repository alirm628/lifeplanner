from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.event import Event
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, CategoryBreakdownItem, HeatmapPoint, TrendPoint

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/summary', response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(UTC)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=7)

    events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id, Event.start_time < week_end, Event.end_time > week_start)
        .all()
    )

    planned_minutes = sum(int((event.end_time - event.start_time).total_seconds() // 60) for event in events)
    completed_minutes = sum(event.actual_minutes or 0 for event in events)

    planned_hours = planned_minutes / 60.0
    completed_hours = completed_minutes / 60.0
    missed_hours = max(0.0, planned_hours - completed_hours)

    consistency = min(100.0, (completed_hours / planned_hours) * 100.0) if planned_hours else 0.0
    productivity = min(100.0, ((completed_hours + (planned_hours * 0.2)) / max(1.0, planned_hours)) * 100.0)

    return AnalyticsSummary(
        planned_hours=round(planned_hours, 2),
        completed_hours=round(completed_hours, 2),
        missed_hours=round(missed_hours, 2),
        consistency_score=round(consistency, 2),
        productivity_score=round(productivity, 2),
    )


@router.get('/breakdown', response_model=list[CategoryBreakdownItem])
def analytics_breakdown(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = {c.id: c.name for c in db.query(Category).filter(Category.user_id == current_user.id).all()}
    events = db.query(Event).filter(Event.user_id == current_user.id).all()

    planned: dict[str, float] = {}
    completed: dict[str, float] = {}
    for event in events:
        label = categories.get(event.category_id, 'Uncategorized')
        planned[label] = planned.get(label, 0.0) + ((event.end_time - event.start_time).total_seconds() / 3600)
        completed[label] = completed.get(label, 0.0) + ((event.actual_minutes or 0) / 60.0)

    names = sorted(set(planned.keys()) | set(completed.keys()))
    return [
        CategoryBreakdownItem(
            category=name,
            planned_hours=round(planned.get(name, 0.0), 2),
            completed_hours=round(completed.get(name, 0.0), 2),
        )
        for name in names
    ]


@router.get('/trends', response_model=list[TrendPoint])
def analytics_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(UTC)
    result: list[TrendPoint] = []

    for weeks_ago in range(7, -1, -1):
        start = (now - timedelta(days=now.weekday())) - timedelta(days=7 * weeks_ago)
        end = start + timedelta(days=7)
        events = (
            db.query(Event)
            .filter(Event.user_id == current_user.id, Event.start_time < end, Event.end_time > start)
            .all()
        )
        planned_hours = sum((event.end_time - event.start_time).total_seconds() / 3600 for event in events)
        completed_hours = sum((event.actual_minutes or 0) / 60.0 for event in events)

        result.append(
            TrendPoint(
                label=start.date().isoformat(),
                planned_hours=round(planned_hours, 2),
                completed_hours=round(completed_hours, 2),
            )
        )

    return result


@router.get('/heatmap', response_model=list[HeatmapPoint])
def analytics_heatmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    buckets: dict[tuple[int, int], int] = {}

    for event in events:
        key = (event.start_time.weekday(), event.start_time.hour)
        buckets[key] = buckets.get(key, 0) + 1

    return [HeatmapPoint(weekday=day, hour=hour, count=count) for (day, hour), count in sorted(buckets.items())]
