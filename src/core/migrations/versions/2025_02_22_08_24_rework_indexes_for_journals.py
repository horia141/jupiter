"""Rework indexes for journals

Revision ID: a425d5a0c731
Revises: 9dabd2175730
Create Date: 2025-02-22 08:24:24.376672

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "a425d5a0c731"
down_revision = "9dabd2175730"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing index
    with op.batch_alter_table("journal") as batch_op:
        batch_op.drop_index("ix_journal_journal_collection_ref_id_right_now")

    # Create the new index
    op.execute(
        """
        CREATE UNIQUE INDEX ix_journal_journal_collection_ref_id_period_right_now
        ON journal (journal_collection_ref_id, period, right_now)
        WHERE archived=0
    """
    )


def downgrade():
    pass
