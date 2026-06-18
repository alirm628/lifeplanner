from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.event import Event
from app.models.goal import Goal
from app.models.task import Task
from app.models.template import ScheduleTemplate
from app.models.user import User
from app.schemas.search import SearchResponse, SearchResultItem

router = APIRouter(prefix='/search', tags=['search'])


@router.get('', response_model=SearchResponse)
def global_search(q: str = Query(min_length=1), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results: list[SearchResultItem] = []

    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.title.ilike(f'%{q}%')).limit(10).all()
    events = db.query(Event).filter(Event.user_id == current_user.id, Event.title.ilike(f'%{q}%')).limit(10).all()
    categories = db.query(Category).filter(Category.user_id == current_user.id, Category.name.ilike(f'%{q}%')).limit(10).all()
    goals = db.query(Goal).filter(Goal.user_id == current_user.id, Goal.title.ilike(f'%{q}%')).limit(10).all()
    templates = db.query(ScheduleTemplate).filter(ScheduleTemplate.user_id == current_user.id, ScheduleTemplate.name.ilike(f'%{q}%')).limit(10).all()

    for item in tasks:
        results.append(SearchResultItem(id=item.id, type='task', title=item.title, subtitle=item.status.value))
    for item in events:
        results.append(SearchResultItem(id=item.id, type='event', title=item.title, subtitle=item.start_time.isoformat()))
    for item in categories:
        results.append(SearchResultItem(id=item.id, type='category', title=item.name, subtitle=f'{item.weekly_target_hours}h/week'))
    for item in goals:
        results.append(SearchResultItem(id=item.id, type='goal', title=item.title, subtitle=item.status.value))
    for item in templates:
        results.append(SearchResultItem(id=item.id, type='template', title=item.name, subtitle=item.description))

    return SearchResponse(results=results[:50])
