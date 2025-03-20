"""Backfill dates for time plans

Revision ID: 2be36a76f15d
Revises: 6f4afe696ea8
Create Date: 2024-05-28 18:55:24.741239

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2be36a76f15d"
down_revision = "6f4afe696ea8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("time_plan") as batch_op:
        batch_op.add_column(sa.Column("start_date", sa.Date, nullable=True))
        batch_op.add_column(sa.Column("end_date", sa.Date, nullable=True))
    op.execute(
        """
        UPDATE time_plan
        SET start_date = right_now, end_date = right_now
        """
    )


def downgrade() -> None:
    pass
