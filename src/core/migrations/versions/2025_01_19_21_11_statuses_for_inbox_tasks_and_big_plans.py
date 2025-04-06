"""Statuses for inbox tasks and big plans

Revision ID: 5d8f4dea8ebb
Revises: 1bfa3e606695
Create Date: 2025-01-19 21:11:26.733509

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "5d8f4dea8ebb"
down_revision = "1bfa3e606695"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE inbox_task
        SET status = 'not-started'
        WHERE status = 'accepted';
        """
    )
    op.execute(
        """
        UPDATE inbox_task
        SET status = 'not-started-gen'
        WHERE status = 'recurring';
        """
    )
    op.execute(
        """
        UPDATE big_plan
        SET status = 'not-started'
        WHERE status = 'accepted';
        """
    )


def downgrade() -> None:
    pass
