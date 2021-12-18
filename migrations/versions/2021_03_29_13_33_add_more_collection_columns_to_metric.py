"""Add more collection columns to metric

Revision ID: 23912567470d
Revises: 834b07e1bb4f
Create Date: 2021-03-29 13:33:03.031792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23912567470d'
down_revision = '834b07e1bb4f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metric', sa.Column('collection_eisen', sa.JSON, nullable=True))
    op.add_column('metric', sa.Column('collection_difficulty', sa.String, nullable=True))
    op.add_column('metric', sa.Column('collection_actionable_from_day', sa.Integer, nullable=True))
    op.add_column('metric', sa.Column('collection_actionable_from_month', sa.Integer, nullable=True))
    op.add_column('metric', sa.Column('collection_due_at_time', sa.String, nullable=True))
    op.add_column('metric', sa.Column('collection_due_at_day', sa.Integer, nullable=True))
    op.add_column('metric', sa.Column('collection_due_at_month', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('metric', 'collection_eisen')
    op.drop_column('metric', 'collection_difficulty')
    op.drop_column('metric', 'collection_actionable_from_day')
    op.drop_column('metric', 'collection_actionable_from_month')
    op.drop_column('metric', 'collection_due_at_time')
    op.drop_column('metric', 'collection_due_at_day')
    op.drop_column('metric', 'collection_due_at_month')
