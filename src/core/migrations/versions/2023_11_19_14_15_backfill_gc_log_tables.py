"""Backfill GC log tables

Revision ID: 98898cddadae
Revises: 4638d68a087a
Create Date: 2023-11-19 14:15:17.608364

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "98898cddadae"
down_revision = "4638d68a087a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO gc_log
        SELECT
            ref_id as ref_id,
            1 as version,
            0 as archived,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            ref_id as workspace_ref_id
        FROM workspace;
    """
    )
    op.execute(
        """
        INSERT INTO gc_log_event
        SELECT
            ref_id as owner_ref_id,
            created_time as timestamp,
            0 as session_index,
            'Created' as name,
            'CLI' as source,
            1 as owner_version,
            'Created' as kind,
            '{}}' as data
        FROM workspace;
    """
    )


def downgrade() -> None:
    pass
