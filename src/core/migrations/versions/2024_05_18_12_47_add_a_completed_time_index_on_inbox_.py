"""Add a completed time index on inbox tasks

Revision ID: 1e84ca5c697c
Revises: 9b7407229de1
Create Date: 2024-05-18 12:47:04.458005

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1e84ca5c697c"
down_revision = "9b7407229de1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_inbox_task_inbox_task_collection_ref_id_completed_time ON inbox_task (inbox_task_collection_ref_id, completed_time)
        WHERE completed_time IS NOT NULL
    """
    )


def downgrade() -> None:
    pass
