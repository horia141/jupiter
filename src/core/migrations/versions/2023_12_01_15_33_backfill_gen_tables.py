"""Backfill gen tables

Revision ID: 90a028e24c30
Revises: e743ba3afcea
Create Date: 2023-12-01 15:33:04.522257

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "90a028e24c30"
down_revision = "e743ba3afcea"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO gen_log
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
        INSERT INTO gen_log_event
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


def downgrade():
    pass
