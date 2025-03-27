"""Fix borked dates

Revision ID: 826b23bc949e
Revises: fe4d41b0a856
Create Date: 2025-03-21 23:28:05.697368

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "826b23bc949e"
down_revision = "fe4d41b0a856"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE inbox_task
        SET actionable_date = DATE(actionable_date)
        WHERE actionable_date IS NOT NULL;
    """
    )

    op.execute(
        """
        UPDATE inbox_task
        SET due_date = DATE(due_date)
        WHERE due_date IS NOT NULL;
    """
    )

    op.execute(
        """
        UPDATE chore
        SET start_at_date = DATE(start_at_date)
        WHERE start_at_date IS NOT NULL;
    """
    )

    op.execute(
        """
        UPDATE chore
        SET end_at_date = DATE(end_at_date)
        WHERE end_at_date IS NOT NULL;
    """
    )

    op.execute(
        """
        UPDATE big_plan
        SET actionable_date = DATE(actionable_date)
        WHERE actionable_date IS NOT NULL;
    """
    )

    op.execute(
        """
        UPDATE big_plan
        SET due_date = DATE(due_date)
        WHERE due_date IS NOT NULL;
    """
    )


def downgrade() -> None:
    pass
