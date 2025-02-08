"""Change skip rule from none to null

Revision ID: 8ff19872296e
Revises: c3b952bcd8c2
Create Date: 2025-02-07 22:42:48.982913

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8ff19872296e"
down_revision = "c3b952bcd8c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            UPDATE habit
            SET skip_rule = NULL
            WHERE skip_rule = 'none';
        """
    )
    op.execute(
        """
            UPDATE chore
            SET skip_rule = NULL
            WHERE skip_rule = 'none';
        """
    )


def downgrade():
    pass
