"""Backfill journal collection

Revision ID: 008a3a72fb29
Revises: accd87afae45
Create Date: 2024-01-03 00:52:41.294834

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "008a3a72fb29"
down_revision = "accd87afae45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO journal_collection
               SELECT
                   ref_id as ref_id,
                   1 as version,
                   0 as archived,
                   created_time as created_time,
                   created_time as last_modified_time,
                   null as archived_time,
                   ref_id as workspace_ref_id,
                   '["monthly"]' as periods,
                   default_project_ref_id as writing_task_project_ref_id,
                   'important' as writing_task_eisen,
                   'medium' as writing_task_difficulty
               FROM workspace;
        """
    )
    op.execute(
        """
        INSERT INTO journal_collection_event
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
