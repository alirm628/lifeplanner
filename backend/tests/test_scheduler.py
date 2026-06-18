from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.category import Category
from app.models.enums import EventType, LockMode, ScheduleMode
from app.models.event import Event
from app.models.setting import UserSetting
from app.models.user import User
from app.services.scheduler import generate_schedule


def _make_session():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_scheduler_respects_locked_fixed_blocks():
    db = _make_session()

    user = User(email='u@test.dev', hashed_password='x', is_active=True)
    db.add(user)
    db.flush()

    db.add(UserSetting(user_id=user.id, workday_start_hour=8, workday_end_hour=20))
    category = Category(
        user_id=user.id,
        name='Study',
        weekly_target_hours=4,
        session_length_minutes=60,
        priority=2,
        min_session_minutes=60,
        max_session_minutes=120,
    )
    db.add(category)
    db.flush()

    monday = date.today() - timedelta(days=date.today().weekday())
    fixed_start = datetime.combine(monday, datetime.min.time()).replace(hour=9)
    fixed_end = fixed_start + timedelta(hours=3)

    db.add(
        Event(
            user_id=user.id,
            category_id=category.id,
            title='Class',
            start_time=fixed_start,
            end_time=fixed_end,
            event_type=EventType.fixed,
            lock_mode=LockMode.locked,
        )
    )
    db.commit()

    proposed, diagnostics = generate_schedule(db, user.id, monday, ScheduleMode.full_auto)

    fixed = [e for e in proposed if e['event_type'] == 'fixed']
    flexible = [e for e in proposed if e['event_type'] == 'flexible']

    assert len(fixed) == 1
    assert len(flexible) >= 1
    assert diagnostics['total_target_hours'] >= 4

    for event in flexible:
        start = datetime.fromisoformat(event['start_time'])
        end = datetime.fromisoformat(event['end_time'])
        assert not (start < fixed_end and fixed_start < end)

    db.close()


def test_exact_block_length_and_round_up_remainder():
    db = _make_session()
    user = User(email='u2@test.dev', hashed_password='x', is_active=True)
    db.add(user)
    db.flush()

    db.add(UserSetting(user_id=user.id, workday_start_hour=8, workday_end_hour=22, min_gap_between_flexible_minutes=30))
    category = Category(
        user_id=user.id,
        name='Gym',
        weekly_target_hours=2.5,
        session_length_minutes=60,
        priority=3,
    )
    db.add(category)
    db.commit()

    monday = date.today() - timedelta(days=date.today().weekday())
    proposed, _ = generate_schedule(db, user.id, monday, ScheduleMode.full_auto)

    blocks = [event for event in proposed if event['event_type'] == 'flexible' and event['category_id'] == category.id]
    assert len(blocks) >= 3  # ceil(150/60) = 3 blocks

    for block in blocks:
        duration = datetime.fromisoformat(block['end_time']) - datetime.fromisoformat(block['start_time'])
        assert int(duration.total_seconds() // 60) == 60

    db.close()


def test_fill_gaps_preserves_existing_flexible_blocks():
    db = _make_session()
    user = User(email='u3@test.dev', hashed_password='x', is_active=True)
    db.add(user)
    db.flush()

    db.add(UserSetting(user_id=user.id, workday_start_hour=8, workday_end_hour=21))
    category = Category(user_id=user.id, name='Project', weekly_target_hours=6, session_length_minutes=60)
    db.add(category)
    db.flush()

    monday = date.today() - timedelta(days=date.today().weekday())
    existing_start = datetime.combine(monday, datetime.min.time()).replace(hour=10)
    db.add(
        Event(
            user_id=user.id,
            category_id=category.id,
            title='Project',
            start_time=existing_start,
            end_time=existing_start + timedelta(hours=1),
            event_type=EventType.flexible,
            lock_mode=LockMode.unlocked,
        )
    )
    db.commit()

    proposed, _ = generate_schedule(db, user.id, monday, ScheduleMode.fill_gaps)
    preserved = [e for e in proposed if e['event_type'] == 'flexible' and e['start_time'].startswith(existing_start.isoformat()[:16])]

    assert len(preserved) >= 1
    db.close()
