"""Add search tables

Revision ID: fbdcd37bbdae
Revises: 89c2a987db66
Create Date: 2023-08-05 16:36:38.553198

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "fbdcd37bbdae"
down_revision = "89c2a987db66"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    CREATE VIRTUAL TABLE search_index USING fts5(
        workspace_ref_id,
        entity_tag,
        ref_id UNINDEXED, 
        name,
        archived UNINDEXED,
        tokenize="porter unicode61 remove_diacritics 1"
    );
    """
    )
    op.execute(
        """
    INSERT INTO search_index SELECT 
        itc.workspace_ref_id AS workspace_ref_id,
        'InboxTask' as entity_tag,
        it.ref_id as ref_id,
        it.name as name,
        it.archived AS archived
    FROM inbox_task_collection AS itc
    JOIN inbox_task AS it
    ON itc.ref_id=it.inbox_task_collection_ref_id;
    """
    )


def downgrade() -> None:
    op.execute("""drop table if exists search_index""")
