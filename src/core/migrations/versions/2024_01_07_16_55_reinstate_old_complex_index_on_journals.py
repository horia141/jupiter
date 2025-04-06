"""Reinstate old complex index on journals

Revision ID: 7fe68e40aa35
Revises: 700375030fae
Create Date: 2024-01-07 16:55:37.864999

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "7fe68e40aa35"
down_revision = "700375030fae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX ix_journal_journal_collection_ref_id_period_timeline ON journal (journal_collection_ref_id, period, timeline)
        WHERE archived=0;
    """
    )


def downgrade() -> None:
    pass
