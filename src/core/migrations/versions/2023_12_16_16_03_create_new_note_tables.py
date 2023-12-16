"""Create new note tables

Revision ID: 8e317829bf1f
Revises: 6e41a5149068
Create Date: 2023-12-16 16:03:39.714376

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8e317829bf1f"
down_revision = "6e41a5149068"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE new_note (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            note_collection_ref_id INTEGER NOT NULL,
            domain VARCHAR(16) NOT NULL,
            source_entity_ref_id INTEGER  NOT NULL,
            content JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (note_collection_ref_id) REFERENCES note_collection (ref_id)
            );
    """
    )

    op.execute(
        """
    INSERT INTO doc
    SELECT
        ref_id,
        1 as version,
        0 archived,
        created_time,
        last_modified_time,
        archived_time,
        note_collection_ref_id as doc_collection_ref_id,
        null as parent_doc_ref_id,
        name as name
    FROM note WHERE source='user';"""
    )

    op.execute(
        """
        INSERT INTO doc_event
                SELECT
                    ref_id as owner_ref_id,
                    created_time as timestamp,
                    0 as session_index,
                    'Created' as name,
                    'CLI' as source,
                    1 as owner_version,
                    'Created' as kind,
                    '{}}' as data
                FROM note WHERE source='user';
        """
    )

    op.execute(
        """
    INSERT INTO new_note
    SELECT
        ref_id,
        version,
        archived,
        created_time,
        last_modified_time,
        archived_time,
        note_collection_ref_id,
        'docs' as domain,
        ref_id as source_entity_ref_id,
        content
    FROM note WHERE source='user';
               """
    )

    op.execute(
        """
    INSERT INTO new_note
    SELECT
        ref_id,
        version,
        archived,
        created_time,
        last_modified_time,
        archived_time,
        note_collection_ref_id,
        source as domain,
        source_entity_ref_id,
        content
    FROM note WHERE source is not'user';
               """
    )

    op.execute("""DROP TABLE note;""")

    op.execute(
        """
        CREATE TABLE note (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            note_collection_ref_id INTEGER NOT NULL,
            domain VARCHAR(16) NOT NULL,
            source_entity_ref_id INTEGER  NOT NULL,
            content JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (note_collection_ref_id) REFERENCES note_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_note_note_collection_ref_id ON note (note_collection_ref_id);
    """
    )
    op.execute(
        """
    CREATE UNIQUE INDEX ix_note_domain_source_entity_ref_id ON note (domain, source_entity_ref_id);
    """
    )
    op.execute(
        """
        INSERT INTO note SELECT * FROM new_note;
    """
    )
    op.execute("""DROP TABLE new_note;""")


def downgrade():
    op.execute("""DROP TABLE IF EXISTS new_note""")
