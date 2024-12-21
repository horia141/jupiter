"""Add project column for order of children

Revision ID: 7fd41e13e30f
Revises: d1157bf2d79a
Create Date: 2024-03-24 17:36:43.118354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7fd41e13e30f"
down_revision = "d1157bf2d79a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("project") as batch_op:
        batch_op.add_column(
            sa.Column("order_of_child_projects", sa.JSON, nullable=True)
        )


def downgrade() -> None:
    pass
