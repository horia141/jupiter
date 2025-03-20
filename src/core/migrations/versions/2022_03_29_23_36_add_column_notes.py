"""Add column notes

Revision ID: d9629228f17e
Revises: 346d70771b6f
Create Date: 2022-03-29 23:36:23.561019

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d9629228f17e"
down_revision = "346d70771b6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inbox_task", sa.Column("notes", sa.Unicode(), nullable=True))


def downgrade() -> None:
    pass
