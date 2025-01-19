"""Update tasks of not-started status

Revision ID: 0ea1b53062ca
Revises: f858598fb7b3
Create Date: 2025-01-19 20:30:47.537295

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0ea1b53062ca"
down_revision = "f858598fb7b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE inbox_task
        SET status = 'accepted'
        WHERE status = 'not-started';
        """
    )


def downgrade() -> None:
    pass
