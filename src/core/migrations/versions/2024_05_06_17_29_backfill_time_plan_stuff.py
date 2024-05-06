"""Backfill time plan stuff

Revision ID: 9b7407229de1
Revises: eb965cd038e5
Create Date: 2024-05-06 17:29:04.758093

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9b7407229de1"
down_revision = "eb965cd038e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO time_plan_domain
               SELECT
                   ref_id as ref_id,
                   1 as version,
                   0 as archived,
                   created_time as created_time,
                   created_time as last_modified_time,
                   null as archived_time,
                   ref_id as workspace_ref_id,
                   7 as days_until_gc
               FROM workspace;
        """
    )
    op.execute(
        """
        INSERT INTO time_plan_domain_event
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
    op.execute(
        """
        UPDATE workspace
        SET feature_flags = json_set(feature_flags, '$.time-plans', 'true')
        """
    )


def downgrade() -> None:
    pass
