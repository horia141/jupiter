"""Update big plans of not-started status

Revision ID: 1bfa3e606695
Revises: 0ea1b53062ca
Create Date: 2025-01-19 20:45:49.578552

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "1bfa3e606695"
down_revision = "0ea1b53062ca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE big_plan
        SET status = 'accepted'
        WHERE status = 'not-started';
        """
    )


def downgrade() -> None:
    pass
