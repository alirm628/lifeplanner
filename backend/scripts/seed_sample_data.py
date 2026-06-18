from datetime import datetime, timedelta
import random

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.category import Category
from app.models.enums import EventType, LockMode
from app.models.event import Event
from app.models.setting import UserSetting
from app.models.user import User


CATEGORIES = [
    ('School', '#0ea5e9', 10),
    ('BiteSurge', '#22c55e', 10),
    ('Gym', '#ef4444', 6),
    ('Violin', '#a855f7', 2),
    ('Friends', '#f97316', 4),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    user = db.query(User).filter(User.email == 'demo@lifeplanner.local').first()
    if not user:
        user = User(email='demo@lifeplanner.local', hashed_password=get_password_hash('demo1234'), is_active=True)
        db.add(user)
        db.flush()

    if not db.query(UserSetting).filter(UserSetting.user_id == user.id).first():
        db.add(UserSetting(user_id=user.id))

    existing = db.query(Category).filter(Category.user_id == user.id).count()
    if existing == 0:
        for name, color, target in CATEGORIES:
            db.add(
                Category(
                    user_id=user.id,
                    name=name,
                    color=color,
                    priority=2,
                    weekly_target_hours=target,
                    session_length_minutes=60,
                    min_session_minutes=45,
                    max_session_minutes=120,
                    preferred_days='mon,tue,wed,thu,fri',
                    preferred_times='morning',
                )
            )

    db.flush()
    categories = db.query(Category).filter(Category.user_id == user.id).all()

    start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    week_start = start - timedelta(days=start.weekday())

    if db.query(Event).filter(Event.user_id == user.id).count() == 0:
        for day in range(5):
            class_start = week_start + timedelta(days=day, hours=9)
            db.add(
                Event(
                    user_id=user.id,
                    title='Class',
                    start_time=class_start,
                    end_time=class_start + timedelta(hours=2),
                    event_type=EventType.fixed,
                    lock_mode=LockMode.locked,
                    category_id=categories[0].id,
                )
            )

        for _ in range(20):
            category = random.choice(categories)
            day = random.randint(0, 6)
            hour = random.randint(10, 20)
            duration = random.choice([60, 90, 120])
            start_at = week_start + timedelta(days=day, hours=hour)
            db.add(
                Event(
                    user_id=user.id,
                    title=category.name,
                    start_time=start_at,
                    end_time=start_at + timedelta(minutes=duration),
                    event_type=EventType.flexible,
                    lock_mode=LockMode.unlocked,
                    category_id=category.id,
                )
            )

    db.commit()
    db.close()
    print('Sample data ready: demo@lifeplanner.local / demo1234')


if __name__ == '__main__':
    seed()
