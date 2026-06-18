"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa


revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('weekly_target_hours', sa.Float(), nullable=False),
        sa.Column('min_session_minutes', sa.Integer(), nullable=False),
        sa.Column('max_session_minutes', sa.Integer(), nullable=False),
        sa.Column('preferred_days', sa.String(length=64), nullable=True),
        sa.Column('preferred_times', sa.String(length=64), nullable=True),
        sa.Column('default_location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timezone', sa.String(length=64), nullable=False),
        sa.Column('workday_start_hour', sa.Integer(), nullable=False),
        sa.Column('workday_end_hour', sa.Integer(), nullable=False),
        sa.Column('sleep_start_hour', sa.Integer(), nullable=False),
        sa.Column('sleep_end_hour', sa.Integer(), nullable=False),
        sa.Column('energy_windows', sa.JSON(), nullable=False),
        sa.Column('break_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('meal_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('commute_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('prep_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=True)

    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.Enum('fixed', 'flexible', name='eventtype'), nullable=False),
        sa.Column('lock_mode', sa.Enum('unlocked', 'locked', 'pinned_day', 'pinned_time', 'pinned_day_time', name='lockmode'), nullable=False),
        sa.Column('recurrence_rule', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('actual_minutes', sa.Integer(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_events_category_id'), 'events', ['category_id'], unique=False)
    op.create_index(op.f('ix_events_end_time'), 'events', ['end_time'], unique=False)
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_start_time'), 'events', ['start_time'], unique=False)
    op.create_index(op.f('ix_events_user_id'), 'events', ['user_id'], unique=False)

    op.create_table(
        'schedule_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('mode', sa.Enum('full_auto', 'respect_locks', name='schedulemode'), nullable=False),
        sa.Column('proposed_events', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_schedule_runs_id'), 'schedule_runs', ['id'], unique=False)
    op.create_index(op.f('ix_schedule_runs_user_id'), 'schedule_runs', ['user_id'], unique=False)
    op.create_index(op.f('ix_schedule_runs_week_start'), 'schedule_runs', ['week_start'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_schedule_runs_week_start'), table_name='schedule_runs')
    op.drop_index(op.f('ix_schedule_runs_user_id'), table_name='schedule_runs')
    op.drop_index(op.f('ix_schedule_runs_id'), table_name='schedule_runs')
    op.drop_table('schedule_runs')

    op.drop_index(op.f('ix_events_user_id'), table_name='events')
    op.drop_index(op.f('ix_events_start_time'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_index(op.f('ix_events_end_time'), table_name='events')
    op.drop_index(op.f('ix_events_category_id'), table_name='events')
    op.drop_table('events')

    op.drop_index(op.f('ix_user_settings_user_id'), table_name='user_settings')
    op.drop_table('user_settings')

    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
