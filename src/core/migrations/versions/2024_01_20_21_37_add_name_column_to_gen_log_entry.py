"""Add name column to gen_log_entry

Revision ID: b8fd63171df8
Revises: 3fbd062599c6
Create Date: 2024-01-20 21:37:41.761707

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8fd63171df8"
down_revision = "3fbd062599c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("gen_log_entry") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade() -> None:
    pass
