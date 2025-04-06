"""Move notes into separate tables

Revision ID: 89d9d7551d95
Revises: 4d1bac2408cf
Create Date: 2023-12-03 16:59:51.092653

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "89d9d7551d95"
down_revision = "4d1bac2408cf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO note SELECT
            null as ref_id,
            1 as version,
            false as archived,
            c.created_time as created_time,
            c.last_modified_time as last_modified_time,
            null as archived_time,
            m.metric_collection_ref_id as note_collection_ref_id, --hack
            null as parent_note_ref_id,
            'metric-entry' as source,
            c.ref_id as source_entity_ref_id,
            'Note for metric "' || m.name || '" on ' || strftime('%Y-%m-%d', c.collection_time) as name,
            json_array(
               json_object(
                'kind', 'paragraph',
                'correlation_id', '1',
               'text', c.notes
               )
            ) as content
        FROM metric_entry AS c
        JOIN metric AS m
        ON m.ref_id = c.metric_ref_id
        WHERE c.notes IS NOT null AND c.notes != '';
    """
    )


def downgrade() -> None:
    pass
