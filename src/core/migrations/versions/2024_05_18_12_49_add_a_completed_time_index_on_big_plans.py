"""Add a completed time index on big plans

Revision ID: 6f4afe696ea8
Revises: 1e84ca5c697c
Create Date: 2024-05-18 12:49:21.636230

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6f4afe696ea8"
down_revision = "1e84ca5c697c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_big_plan_big_plan_collection_ref_id_completed_time ON big_plan (big_plan_collection_ref_id, completed_time)
        WHERE completed_time IS NOT NULL
    """
    )


def downgrade() -> None:
    pass
