"""Backfill notes

Revision ID: 4d1bac2408cf
Revises: 90a028e24c30
Create Date: 2023-12-02 21:53:14.441458

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "4d1bac2408cf"
down_revision = "90a028e24c30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    INSERT INTO search_index SELECT 
        c.workspace_ref_id AS workspace_ref_id,
        'Note' AS entity_tag,
        c.ref_id AS parent_ref_id,
        e.ref_id AS ref_id,
        e.name AS name,
        e.archived AS archived,
        e.created_time AS created_time,
        e.last_modified_time AS last_modified_time,
        e.archived_time AS archived_time
    FROM note_collection AS c
    JOIN note AS e
    ON c.ref_id=e.note_collection_ref_id
    WHERE e.ref_id NOT IN (
        SELECT ref_id
        FROM search_index
        WHERE entity_tag='Note'
    )
    """
    )


def downgrade() -> None:
    pass
