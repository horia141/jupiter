"""Notes tables

Revision ID: 055389992beb
Revises: 20c0c83a38a8
Create Date: 2023-08-25 08:44:57.749985

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "055389992beb"
down_revision = "20c0c83a38a8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE note_collection (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_note_collection_workspace_ref_id ON note_collection (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE note_collection_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES note_collection (ref_id)
            );
    """
    )
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
            parent_note_ref_id INTEGER,
            source VARCHAR(16) NOT NULL,
            source_entity_ref_id INTEGER,
            name VARCHAR(64) NOT NULL,
            content JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (note_collection_ref_id) REFERENCES note_collection (ref_id),
            FOREIGN KEY (parent_note_ref_id) REFERENCES note (ref_id)
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
        CREATE INDEX ix_note_parent_note_ref_id ON note (parent_note_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE note_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES note (ref_id)
            );
    """
    )


def downgrade():
    op.execute("""DROP TABLE IF EXISTS note_event""")
    op.execute("""DROP TABLE IF EXISTS note""")
    op.execute("""DROP TABLE IF EXISTS note_collection_event""")
    op.execute("""DROP TABLE IF EXISTS note_collection""")
