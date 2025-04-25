"""Add structures for journal stats

Revision ID: e02518a0fcc7
Revises: baf2d13b02f8
Create Date: 2025-04-25 23:45:12.620912

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "e02518a0fcc7"
down_revision = "baf2d13b02f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE journal_stats (
            journal_ref_id INTEGER NOT NULL,
            report JSON NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            FOREIGN KEY (journal_ref_id) REFERENCES journal (ref_id),
            UNIQUE (journal_ref_id)
        );
        """
    )

    op.execute(
        """
        INSERT INTO journal_stats
        SELECT
            ref_id as journal_ref_id,
            report as report,
            created_time as created_time,
            created_time as last_modified_time
        FROM journal;
        """
    )

    with op.batch_alter_table("journal") as batch_op:
        batch_op.drop_column("report")


def downgrade() -> None:
    op.drop_table("journal_stats")
