from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.enums import EventType, GoalStatus, LockMode, TaskStatus
from app.models.event import Event
from app.models.goal import Goal
from app.models.setting import UserSetting
from app.models.task import Task
from app.models.template import ScheduleTemplate
from app.models.user import User

router = APIRouter(prefix='/backup', tags=['backup'])


@router.get('/export')
def export_backup(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    templates = db.query(ScheduleTemplate).filter(ScheduleTemplate.user_id == current_user.id).all()
    settings = db.query(UserSetting).filter(UserSetting.user_id == current_user.id).first()

    return {
        'exported_at': datetime.utcnow().isoformat(),
        'user': {'id': current_user.id, 'email': current_user.email},
        'settings': {
            'timezone': settings.timezone if settings else 'America/New_York',
            'workday_start_hour': settings.workday_start_hour if settings else 8,
            'workday_end_hour': settings.workday_end_hour if settings else 22,
            'sleep_start_hour': settings.sleep_start_hour if settings else 23,
            'sleep_end_hour': settings.sleep_end_hour if settings else 7,
            'energy_windows': settings.energy_windows if settings else {},
            'break_buffer_minutes': settings.break_buffer_minutes if settings else 10,
            'meal_buffer_minutes': settings.meal_buffer_minutes if settings else 30,
            'commute_buffer_minutes': settings.commute_buffer_minutes if settings else 15,
            'prep_buffer_minutes': settings.prep_buffer_minutes if settings else 10,
            'min_gap_between_flexible_minutes': settings.min_gap_between_flexible_minutes if settings else 30,
            'max_flexible_minutes_per_day': settings.max_flexible_minutes_per_day if settings else 360,
            'max_same_category_blocks_per_day': settings.max_same_category_blocks_per_day if settings else 2,
        },
        'categories': [
            {
                'name': c.name,
                'color': c.color,
                'description': c.description,
                'priority': c.priority,
                'weekly_target_hours': c.weekly_target_hours,
                'max_blocks_per_day': c.max_blocks_per_day,
                'session_length_minutes': c.session_length_minutes,
                'min_session_minutes': c.min_session_minutes,
                'max_session_minutes': c.max_session_minutes,
                'preferred_days': c.preferred_days,
                'preferred_times': c.preferred_times,
                'default_location': c.default_location,
            }
            for c in categories
        ],
        'events': [
            {
                'title': e.title,
                'description': e.description,
                'notes': e.notes,
                'start_time': e.start_time.isoformat(),
                'end_time': e.end_time.isoformat(),
                'event_type': e.event_type.value,
                'lock_mode': e.lock_mode.value,
                'recurrence_rule': e.recurrence_rule,
                'location': e.location,
                'estimated_minutes': e.estimated_minutes,
                'actual_minutes': e.actual_minutes,
                'category_id': e.category_id,
            }
            for e in events
        ],
        'tasks': [
            {
                'title': t.title,
                'description': t.description,
                'notes': t.notes,
                'priority': t.priority,
                'status': t.status.value,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'estimated_minutes': t.estimated_minutes,
                'actual_minutes': t.actual_minutes,
                'category_id': t.category_id,
                'tags': t.tags,
            }
            for t in tasks
        ],
        'goals': [
            {
                'title': g.title,
                'description': g.description,
                'category_id': g.category_id,
                'target_hours': g.target_hours,
                'target_sessions': g.target_sessions,
                'target_date': g.target_date.isoformat() if g.target_date else None,
                'status': g.status.value,
            }
            for g in goals
        ],
        'templates': [
            {
                'name': t.name,
                'description': t.description,
                'template_data': t.template_data,
            }
            for t in templates
        ],
    }


@router.post('/import')
def import_backup(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories_data = payload.get('categories', [])
    events_data = payload.get('events', [])
    tasks_data = payload.get('tasks', [])
    goals_data = payload.get('goals', [])
    templates_data = payload.get('templates', [])

    if not isinstance(categories_data, list) or not isinstance(events_data, list):
        raise HTTPException(status_code=400, detail='Invalid backup payload')

    db.query(Event).filter(Event.user_id == current_user.id).delete()
    db.query(Task).filter(Task.user_id == current_user.id).delete()
    db.query(Goal).filter(Goal.user_id == current_user.id).delete()
    db.query(ScheduleTemplate).filter(ScheduleTemplate.user_id == current_user.id).delete()
    db.query(Category).filter(Category.user_id == current_user.id).delete()

    created_categories: list[Category] = []
    for item in categories_data:
        category = Category(user_id=current_user.id, **item)
        db.add(category)
        created_categories.append(category)

    db.flush()
    cat_map = {i + 1: c.id for i, c in enumerate(created_categories)}

    for event_data in events_data:
        data = dict(event_data)
        source_category_id = data.pop('category_id', None)
        event_type = EventType(data.pop('event_type', 'flexible'))
        lock_mode = LockMode(data.pop('lock_mode', 'unlocked'))
        event = Event(
            user_id=current_user.id,
            category_id=cat_map.get(source_category_id),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            event_type=event_type,
            lock_mode=lock_mode,
            **{k: v for k, v in data.items() if k not in {'start_time', 'end_time'}},
        )
        db.add(event)

    for task_data in tasks_data:
        data = dict(task_data)
        source_category_id = data.pop('category_id', None)
        due_date = datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
        task = Task(
            user_id=current_user.id,
            category_id=cat_map.get(source_category_id),
            due_date=due_date,
            status=TaskStatus(data.get('status', 'todo')),
            **{k: v for k, v in data.items() if k not in {'due_date', 'status'}},
        )
        db.add(task)

    for goal_data in goals_data:
        data = dict(goal_data)
        source_category_id = data.pop('category_id', None)
        target_date = datetime.fromisoformat(data['target_date']).date() if data.get('target_date') else None
        goal = Goal(
            user_id=current_user.id,
            category_id=cat_map.get(source_category_id),
            target_date=target_date,
            status=GoalStatus(data.get('status', 'active')),
            **{k: v for k, v in data.items() if k not in {'target_date', 'status'}},
        )
        db.add(goal)

    for template_data in templates_data:
        template = ScheduleTemplate(user_id=current_user.id, **template_data)
        db.add(template)

    settings_payload = payload.get('settings')
    if isinstance(settings_payload, dict):
        settings = db.query(UserSetting).filter(UserSetting.user_id == current_user.id).first()
        if not settings:
            settings = UserSetting(user_id=current_user.id)
            db.add(settings)
        for key, value in settings_payload.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

    db.commit()
    return {'status': 'ok'}
