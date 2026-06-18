"""v2 scheduler and planning entities

Revision ID: 0002_v2_features
Revises: 0001_initial
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa


revision = '0002_v2_features'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('categories') as batch_op:
        batch_op.add_column(sa.Column('session_length_minutes', sa.Integer(), nullable=False, server_default='60'))

    with op.batch_alter_table('user_settings') as batch_op:
        batch_op.add_column(sa.Column('min_gap_between_flexible_minutes', sa.Integer(), nullable=False, server_default='30'))
        batch_op.add_column(sa.Column('max_flexible_minutes_per_day', sa.Integer(), nullable=False, server_default='360'))
        batch_op.add_column(sa.Column('max_same_category_blocks_per_day', sa.Integer(), nullable=False, server_default='2'))

    op.drop_index('ix_schedule_runs_week_start', table_name='schedule_runs')
    op.drop_index('ix_schedule_runs_user_id', table_name='schedule_runs')
    op.drop_index('ix_schedule_runs_id', table_name='schedule_runs')
    op.drop_table('schedule_runs')

    op.create_table(
        'schedule_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('mode', sa.String(length=40), nullable=False),
        sa.Column('proposed_events', sa.JSON(), nullable=False),
        sa.Column('diagnostics', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_schedule_runs_id'), 'schedule_runs', ['id'], unique=False)
    op.create_index(op.f('ix_schedule_runs_user_id'), 'schedule_runs', ['user_id'], unique=False)
    op.create_index(op.f('ix_schedule_runs_week_start'), 'schedule_runs', ['week_start'], unique=False)

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'done', name='taskstatus'), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True),
        sa.Column('actual_minutes', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_category_id'), 'tasks', ['category_id'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)

    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', name='goalstatus'), nullable=False),
        sa.Column('target_hours', sa.Float(), nullable=True),
        sa.Column('target_sessions', sa.Integer(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)
    op.create_index(op.f('ix_goals_category_id'), 'goals', ['category_id'], unique=False)

    op.create_table(
        'schedule_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_schedule_templates_id'), 'schedule_templates', ['id'], unique=False)
    op.create_index(op.f('ix_schedule_templates_user_id'), 'schedule_templates', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_schedule_templates_user_id'), table_name='schedule_templates')
    op.drop_index(op.f('ix_schedule_templates_id'), table_name='schedule_templates')
    op.drop_table('schedule_templates')

    op.drop_index(op.f('ix_goals_category_id'), table_name='goals')
    op.drop_index(op.f('ix_goals_user_id'), table_name='goals')
    op.drop_index(op.f('ix_goals_id'), table_name='goals')
    op.drop_table('goals')

    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_category_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')

    op.drop_index(op.f('ix_schedule_runs_week_start'), table_name='schedule_runs')
    op.drop_index(op.f('ix_schedule_runs_user_id'), table_name='schedule_runs')
    op.drop_index(op.f('ix_schedule_runs_id'), table_name='schedule_runs')
    op.drop_table('schedule_runs')

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

    with op.batch_alter_table('user_settings') as batch_op:
        batch_op.drop_column('max_same_category_blocks_per_day')
        batch_op.drop_column('max_flexible_minutes_per_day')
        batch_op.drop_column('min_gap_between_flexible_minutes')

    with op.batch_alter_table('categories') as batch_op:
        batch_op.drop_column('session_length_minutes')
