"""Backfill missed schedule rows

Revision ID: 9418c38d5709
Revises: 99c845816b0b
Create Date: 2025-01-25 18:17:08.021306

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9418c38d5709"
down_revision = "99c845816b0b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO schedule_external_sync_log
        SELECT
            ref_id as ref_id,
            1 as version,
            0 as archived,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            schedule_domain_ref_id as schedule_domain_ref_id,
            'not_used' as name
        FROM (
            SELECT
              sd.ref_id + 1000 as ref_id,
              sd.ref_id as schedule_domain_ref_id,
              w.created_time as created_time
            FROM workspace w 
            JOIN schedule_domain sd
            ON w.ref_id=sd.workspace_ref_id
            WHERE sd.ref_id NOT IN (SELECT schedule_domain_ref_id FROM schedule_external_sync_log)
        );
        """
    )
    op.execute(
        """
        INSERT INTO schedule_external_sync_log_event
        SELECT
            ref_id as owner_ref_id,
            created_time as timestamp,
            0 as session_index,
            'Created' as name,
            'CLI' as source,
            1 as owner_version,
            'Created' as kind,
            '{}}' as data
        FROM (
            SELECT
              sd.ref_id + 1000 as ref_id,
              sd.ref_id as schedule_domain_ref_id,
              w.created_time as created_time
            FROM workspace w 
            JOIN schedule_domain sd
            ON w.ref_id=sd.workspace_ref_id
            WHERE sd.ref_id NOT IN (SELECT schedule_domain_ref_id FROM schedule_external_sync_log)
        );
        """
    )


def downgrade() -> None:
    pass
