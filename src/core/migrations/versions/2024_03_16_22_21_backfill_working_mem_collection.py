"""Backfill working mem collection

Revision ID: 9dd1fba9fd4e
Revises: 5c9c383c4f89
Create Date: 2024-03-16 22:21:26.391589

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9dd1fba9fd4e"
down_revision = "5c9c383c4f89"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO working_mem_collection
               SELECT
                   ref_id as ref_id,
                   1 as version,
                   0 as archived,
                   created_time as created_time,
                   created_time as last_modified_time,
                   null as archived_time,
                   ref_id as workspace_ref_id,
                   'daily' as generation_period,
                   default_project_ref_id as cleanup_project_ref_id
               FROM workspace;
        """
    )
    op.execute(
        """
        INSERT INTO working_mem_collection_event
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
