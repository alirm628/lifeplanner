from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import EventType, LockMode
from app.models.event import Event
from app.models.schedule_run import ScheduleRun
from app.models.user import User
from app.schemas.scheduler import ScheduleApplyRequest, ScheduleGenerateRequest, ScheduleGenerateResponse
from app.services.scheduler import generate_schedule

router = APIRouter(prefix='/scheduler', tags=['scheduler'])


@router.post('/generate', response_model=ScheduleGenerateResponse)
def generate(
    payload: ScheduleGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proposals, diagnostics = generate_schedule(db, current_user.id, payload.week_start, payload.mode)

    run = ScheduleRun(
        user_id=current_user.id,
        week_start=payload.week_start,
        mode=payload.mode.value,
        proposed_events=proposals,
        diagnostics=diagnostics,
        status='generated',
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return ScheduleGenerateResponse(
        run_id=run.id,
        mode=payload.mode,
        proposed_events=run.proposed_events,
        diagnostics=run.diagnostics,
    )


@router.post('/apply')
def apply_schedule(
    payload: ScheduleApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = db.query(ScheduleRun).filter(ScheduleRun.id == payload.run_id, ScheduleRun.user_id == current_user.id).first()
    if not run:
        raise HTTPException(status_code=404, detail='Schedule run not found')

    week_start_dt = datetime.combine(run.week_start, datetime.min.time())
    week_end_dt = week_start_dt + timedelta(days=7)

    removable = (
        db.query(Event)
        .filter(
            Event.user_id == current_user.id,
            Event.start_time < week_end_dt,
            Event.end_time > week_start_dt,
            Event.event_type == EventType.flexible,
            Event.lock_mode == LockMode.unlocked,
        )
        .all()
    )
    for event in removable:
        db.delete(event)

    for item in run.proposed_events:
        if item['event_type'] != EventType.flexible.value or item['lock_mode'] != LockMode.unlocked.value:
            continue

        event = Event(
            user_id=current_user.id,
            category_id=item.get('category_id'),
            title=item['title'],
            description=item.get('description'),
            notes=item.get('notes'),
            start_time=datetime.fromisoformat(item['start_time']),
            end_time=datetime.fromisoformat(item['end_time']),
            event_type=EventType(item['event_type']),
            lock_mode=LockMode(item['lock_mode']),
            recurrence_rule=item.get('recurrence_rule'),
            location=item.get('location'),
        )
        db.add(event)

    run.status = 'applied'
    db.commit()

    return {'status': 'ok', 'applied_run_id': run.id}
