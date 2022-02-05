"""Add smart list icon column

Revision ID: a4d17eeeac02
Revises: f2b82bd81fca
Create Date: 2022-02-05 19:02:19.597083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d17eeeac02'
down_revision = 'f2b82bd81fca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('smart_list', sa.Column('icon', sa.String(1), nullable=True))


def downgrade() -> None:
    op.drop_column('smart_list', 'icon')
