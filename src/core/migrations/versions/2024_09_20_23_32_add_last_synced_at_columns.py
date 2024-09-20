"""Add last synced at columns

Revision ID: fb960252be47
Revises: 5bd25a8a7c69
Create Date: 2024-09-20 23:32:27.382583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb960252be47"
down_revision = "5bd25a8a7c69"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("schedule_event_full_days") as batch_op:
        batch_op.add_column(
            sa.Column("external_last_synced_at", sa.DateTime(), nullable=True)
        )
    with op.batch_alter_table("schedule_event_in_day") as batch_op:
        batch_op.add_column(
            sa.Column("external_last_synced_at", sa.DateTime(), nullable=True)
        )


def downgrade() -> None:
    pass
