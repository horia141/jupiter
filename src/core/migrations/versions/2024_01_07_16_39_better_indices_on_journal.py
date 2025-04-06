"""Better indices on journal

Revision ID: 700375030fae
Revises: 008a3a72fb29
Create Date: 2024-01-07 16:39:03.373383

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "700375030fae"
down_revision = "008a3a72fb29"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX ix_journal_journal_collection_ref_id_right_now ON journal (journal_collection_ref_id, right_now)
        WHERE archived=0;
    """
    )
    op.execute("""DROP INDEX ix_journal_journal_collection_ref_id_period_timeline;""")


def downgrade() -> None:
    pass
