from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.event import Event
from app.models.goal import Goal
from app.models.task import Task
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get('', response_model=list[CategoryRead])
def list_categories(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Category).filter(Category.user_id == current_user.id)
    if q:
        query = query.filter(Category.name.ilike(f'%{q}%'))
    return query.order_by(Category.priority.asc(), Category.name.asc()).all()


@router.post('', response_model=CategoryRead)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = Category(user_id=current_user.id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch('/{category_id}', response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete('/{category_id}', status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    # Delete all calendar blocks in this category as requested.
    db.query(Event).filter(Event.user_id == current_user.id, Event.category_id == category_id).delete(synchronize_session=False)
    # Keep non-calendar records intact by uncategorizing them.
    db.query(Task).filter(Task.user_id == current_user.id, Task.category_id == category_id).update({Task.category_id: None})
    db.query(Goal).filter(Goal.user_id == current_user.id, Goal.category_id == category_id).update({Goal.category_id: None})

    db.delete(category)
    db.commit()
