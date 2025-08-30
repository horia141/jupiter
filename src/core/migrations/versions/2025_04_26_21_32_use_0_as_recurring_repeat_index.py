"""Use 0 as recurring_repeat_index

Revision ID: 2f3cd88ada12
Revises: cffeab8d94a2
Create Date: 2025-04-26 21:32:33.481857

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "2f3cd88ada12"
down_revision = "cffeab8d94a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE 
            inbox_task
        SET
            recurring_repeat_index = 0 
        WHERE 
            source = 'habit'
        AND recurring_repeat_index IS NULL
    """
    )


def downgrade() -> None:
    pass
