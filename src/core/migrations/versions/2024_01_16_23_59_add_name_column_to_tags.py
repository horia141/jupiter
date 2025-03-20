"""Add name column to tags

Revision ID: e1d79229c3a2
Revises: 7fe68e40aa35
Create Date: 2024-01-16 23:59:22.468836

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e1d79229c3a2"
down_revision = "7fe68e40aa35"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("smart_list_tag") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade():
    pass
