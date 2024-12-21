"""Backfill time events tables

Revision ID: 58dae1452d44
Revises: 5b937ac5ad07
Create Date: 2024-07-07 16:56:12.563348

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "58dae1452d44"
down_revision = "5b937ac5ad07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO time_event_domain
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
        INSERT INTO time_event_domain_event
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
