"""Add the repeats in period column to habits

Revision ID: 12cb0baf46c9
Revises: 155b641a787c
Create Date: 2022-02-16 22:42:58.768989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12cb0baf46c9'
down_revision = '155b641a787c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('habit', sa.Column('repeats_in_period_count', sa.Integer, nullable=True))
    op.add_column('inbox_task', sa.Column('recurring_repeat_index', sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column('habit', 'repeats_in_period_count')
    op.drop_column('inbox_task', 'recurring_repeat_index')
