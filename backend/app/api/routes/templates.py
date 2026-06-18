from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import EventType, LockMode
from app.models.event import Event
from app.models.template import ScheduleTemplate
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateRead, TemplateUpdate

router = APIRouter(prefix='/templates', tags=['templates'])


@router.get('', response_model=list[TemplateRead])
def list_templates(q: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(ScheduleTemplate).filter(ScheduleTemplate.user_id == current_user.id)
    if q:
        query = query.filter(ScheduleTemplate.name.ilike(f'%{q}%'))
    return query.order_by(ScheduleTemplate.created_at.desc()).all()


@router.post('', response_model=TemplateRead)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = ScheduleTemplate(user_id=current_user.id, **payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post('/from-week', response_model=TemplateRead)
def create_template_from_week(
    name: str,
    week_start: str,
    description: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = datetime.fromisoformat(week_start)
    end = start + timedelta(days=7)
    events = (
        db.query(Event)
        .filter(Event.user_id == current_user.id, Event.start_time < end, Event.end_time > start)
        .all()
    )

    template_data = {
        'events': [
            {
                'title': event.title,
                'description': event.description,
                'notes': event.notes,
                'weekday': event.start_time.weekday(),
                'start_hour': event.start_time.hour,
                'start_minute': event.start_time.minute,
                'duration_minutes': int((event.end_time - event.start_time).total_seconds() // 60),
                'event_type': event.event_type.value,
                'lock_mode': event.lock_mode.value,
                'category_id': event.category_id,
                'location': event.location,
            }
            for event in events
        ]
    }

    template = ScheduleTemplate(user_id=current_user.id, name=name, description=description, template_data=template_data)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post('/{template_id}/apply')
def apply_template(template_id: int, week_start: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id, ScheduleTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')

    start = datetime.fromisoformat(week_start)

    for item in template.template_data.get('events', []):
        event_start = start + timedelta(days=int(item['weekday']), hours=int(item['start_hour']), minutes=int(item.get('start_minute', 0)))
        duration = int(item.get('duration_minutes', 60))
        event = Event(
            user_id=current_user.id,
            category_id=item.get('category_id'),
            title=item['title'],
            description=item.get('description'),
            notes=item.get('notes'),
            start_time=event_start,
            end_time=event_start + timedelta(minutes=duration),
            event_type=EventType(item.get('event_type', 'flexible')),
            lock_mode=LockMode(item.get('lock_mode', 'unlocked')),
            location=item.get('location'),
        )
        db.add(event)

    db.commit()
    return {'status': 'ok'}


@router.patch('/{template_id}', response_model=TemplateRead)
def update_template(template_id: int, payload: TemplateUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id, ScheduleTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete('/{template_id}', status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id, ScheduleTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')

    db.delete(template)
    db.commit()
