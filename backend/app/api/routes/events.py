from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import EventType, LockMode
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventDuplicateRequest, EventRead, EventUpdate

router = APIRouter(prefix='/events', tags=['events'])


@router.get('', response_model=list[EventRead])
def list_events(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    q: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Event).filter(Event.user_id == current_user.id)

    if week_start and not week_end:
        week_end = week_start + timedelta(days=7)
    if week_start and week_end:
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.min.time())
        query = query.filter(Event.start_time < week_end_dt, Event.end_time > week_start_dt)
    if q:
        query = query.filter(Event.title.ilike(f'%{q}%'))
    if category_id:
        query = query.filter(Event.category_id == category_id)

    return query.order_by(Event.start_time.asc()).all()


@router.post('', response_model=EventRead)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = Event(user_id=current_user.id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch('/{event_id}', response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    update_data = payload.model_dump(exclude_unset=True)
    changes_time = 'start_time' in update_data or 'end_time' in update_data

    if changes_time and (event.event_type == EventType.fixed or event.lock_mode != LockMode.unlocked):
        raise HTTPException(status_code=400, detail='Fixed or locked events cannot be moved')

    if 'start_time' in update_data and 'end_time' not in update_data and event.end_time > event.start_time:
        original_duration = event.end_time - event.start_time
        update_data['end_time'] = update_data['start_time'] + original_duration

    for key, value in update_data.items():
        setattr(event, key, value)

    if event.end_time <= event.start_time:
        raise HTTPException(status_code=400, detail='end_time must be after start_time')

    db.commit()
    db.refresh(event)
    return event


@router.post('/{event_id}/duplicate', response_model=EventRead)
def duplicate_event(
    event_id: int,
    payload: EventDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    delta = timedelta(days=payload.day_offset)
    new_event = Event(
        user_id=current_user.id,
        category_id=event.category_id,
        title=f'{event.title} (Copy)',
        description=event.description,
        notes=event.notes,
        start_time=event.start_time + delta,
        end_time=event.end_time + delta,
        event_type=event.event_type,
        lock_mode=event.lock_mode,
        recurrence_rule=event.recurrence_rule,
        location=event.location,
        estimated_minutes=event.estimated_minutes,
        actual_minutes=event.actual_minutes,
        extra_data=event.extra_data,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.delete('/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    db.delete(event)
    db.commit()
