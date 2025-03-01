"""Backfill repeats strategy

Revision ID: fe4d41b0a856
Revises: a425d5a0c731
Create Date: 2025-03-01 17:25:16.830824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe4d41b0a856"
down_revision = "a425d5a0c731"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("habit") as batch_op:
        batch_op.add_column(sa.Column("repeats_strategy", sa.String(), nullable=True))
    op.execute(
        """
        UPDATE habit
        SET repeats_strategy = 'all-same'
        WHERE repeats_in_period_count IS NOT NULL
        """
    )


def downgrade():
    pass
