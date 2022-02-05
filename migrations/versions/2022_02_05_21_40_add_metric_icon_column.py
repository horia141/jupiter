"""Add metric icon column

Revision ID: acc4ea807c6d
Revises: a4d17eeeac02
Create Date: 2022-02-05 21:40:47.075716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acc4ea807c6d'
down_revision = 'a4d17eeeac02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('metric', sa.Column('icon', sa.String(1), nullable=True))


def downgrade() -> None:
    op.drop_column('metric', 'icon')
