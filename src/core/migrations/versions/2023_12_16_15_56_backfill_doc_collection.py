"""Backfill doc collection

Revision ID: 6e41a5149068
Revises: 67362331ef94
Create Date: 2023-12-16 15:56:51.602998

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "6e41a5149068"
down_revision = "67362331ef94"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO doc_collection
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
        INSERT INTO doc_collection_event
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
