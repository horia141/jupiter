"""Drop workspace link table

Revision ID: a5a0a1e400dd
Revises: c99c4f461753
Create Date: 2022-01-22 14:48:13.212949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5a0a1e400dd'
down_revision = 'c99c4f461753'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('notion_workspace_link')


def downgrade() -> None:
    pass
