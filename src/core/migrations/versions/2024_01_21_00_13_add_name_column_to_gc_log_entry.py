"""Add name column to gc_log_entry

Revision ID: a4aad54ad575
Revises: b8fd63171df8
Create Date: 2024-01-21 00:13:16.406104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4aad54ad575"
down_revision = "b8fd63171df8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("gc_log_entry") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade() -> None:
    pass
