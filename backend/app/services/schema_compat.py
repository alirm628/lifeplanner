from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


def run_schema_compat(db: Session) -> None:
    bind = db.get_bind()
    inspector = inspect(bind)

    tables = set(inspector.get_table_names())

    if 'categories' in tables:
        cols = {col['name'] for col in inspector.get_columns('categories')}
        if 'session_length_minutes' not in cols:
            db.execute(text("ALTER TABLE categories ADD COLUMN session_length_minutes INTEGER NOT NULL DEFAULT 60"))
        if 'max_blocks_per_day' not in cols:
            db.execute(text("ALTER TABLE categories ADD COLUMN max_blocks_per_day INTEGER"))

    if 'user_settings' in tables:
        cols = {col['name'] for col in inspector.get_columns('user_settings')}
        if 'min_gap_between_flexible_minutes' not in cols:
            db.execute(text("ALTER TABLE user_settings ADD COLUMN min_gap_between_flexible_minutes INTEGER NOT NULL DEFAULT 30"))
        if 'max_flexible_minutes_per_day' not in cols:
            db.execute(text("ALTER TABLE user_settings ADD COLUMN max_flexible_minutes_per_day INTEGER NOT NULL DEFAULT 360"))
        if 'max_same_category_blocks_per_day' not in cols:
            db.execute(text("ALTER TABLE user_settings ADD COLUMN max_same_category_blocks_per_day INTEGER NOT NULL DEFAULT 2"))

    if 'schedule_runs' in tables:
        cols = {col['name'] for col in inspector.get_columns('schedule_runs')}
        if 'diagnostics' not in cols:
            db.execute(text("ALTER TABLE schedule_runs ADD COLUMN diagnostics JSON"))

    db.commit()
