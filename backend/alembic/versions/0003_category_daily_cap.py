"""add per-category daily block cap

Revision ID: 0003_category_daily_cap
Revises: 0002_v2_features
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa


revision = '0003_category_daily_cap'
down_revision = '0002_v2_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('categories') as batch_op:
        batch_op.add_column(sa.Column('max_blocks_per_day', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('categories') as batch_op:
        batch_op.drop_column('max_blocks_per_day')

