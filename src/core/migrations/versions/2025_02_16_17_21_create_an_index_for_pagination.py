"""Create an index for pagination

Revision ID: 9dabd2175730
Revises: 312347a664ec
Create Date: 2025-02-16 17:21:59.144816

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9dabd2175730"
down_revision = "312347a664ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """CREATE INDEX ix_inbox_task_pagination ON inbox_task (inbox_task_collection_ref_id, source, created_time);"""
    )


def downgrade() -> None:
    pass
