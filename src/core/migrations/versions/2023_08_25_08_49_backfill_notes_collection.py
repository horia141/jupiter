"""Backfill notes collection

Revision ID: 6cfc8bf6afac
Revises: 055389992beb
Create Date: 2023-08-25 08:49:24.309162

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6cfc8bf6afac"
down_revision = "055389992beb"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO note_collection
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
        INSERT INTO note_collection_event
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
