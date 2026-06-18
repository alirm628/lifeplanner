from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import EventType, GoalStatus
from app.models.event import Event
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalProgress, GoalRead, GoalUpdate

router = APIRouter(prefix='/goals', tags=['goals'])


@router.get('', response_model=list[GoalRead])
def list_goals(q: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Goal).filter(Goal.user_id == current_user.id)
    if q:
        query = query.filter(Goal.title.ilike(f'%{q}%'))
    return query.order_by(Goal.created_at.desc()).all()


@router.post('', response_model=GoalRead)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = Goal(user_id=current_user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.patch('/{goal_id}', response_model=GoalRead)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail='Goal not found')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)

    db.commit()
    db.refresh(goal)
    return goal


@router.delete('/{goal_id}', status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail='Goal not found')

    db.delete(goal)
    db.commit()


@router.get('/progress', response_model=list[GoalProgress])
def goal_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_end = week_start + timedelta(days=7)

    events = (
        db.query(Event)
        .filter(
            Event.user_id == current_user.id,
            Event.start_time < week_end,
            Event.end_time > week_start,
            Event.event_type == EventType.flexible,
        )
        .all()
    )

    result: list[GoalProgress] = []
    for goal in goals:
        relevant = [event for event in events if goal.category_id is None or event.category_id == goal.category_id]
        minutes = sum(int((event.end_time - event.start_time).total_seconds() // 60) for event in relevant)
        sessions = len(relevant)

        status = goal.status
        if goal.target_hours is not None and minutes / 60 >= goal.target_hours:
            status = GoalStatus.completed
        if goal.target_sessions is not None and sessions >= goal.target_sessions:
            status = GoalStatus.completed

        result.append(
            GoalProgress(
                goal_id=goal.id,
                title=goal.title,
                status=status,
                progress_hours=round(minutes / 60.0, 2),
                progress_sessions=sessions,
                target_hours=goal.target_hours,
                target_sessions=goal.target_sessions,
            )
        )

    return result
