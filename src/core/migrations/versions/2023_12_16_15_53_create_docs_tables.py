"""Create docs tables

Revision ID: 67362331ef94
Revises: 4bbe968a2544
Create Date: 2023-12-16 15:53:22.413742

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "67362331ef94"
down_revision = "4bbe968a2544"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE doc_collection (
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
        CREATE UNIQUE INDEX ix_doc_collection_workspace_ref_id ON doc_collection (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE doc_collection_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES doc_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE TABLE doc (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            doc_collection_ref_id INTEGER NOT NULL,
            parent_doc_ref_id INTEGER,
            name VARCHAR(64) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (doc_collection_ref_id) REFERENCES doc_collection (ref_id),
            FOREIGN KEY (parent_doc_ref_id) REFERENCES doc (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_doc_doc_collection_ref_id ON doc (doc_collection_ref_id);
    """
    )
    op.execute(
        """
        CREATE INDEX ix_doc_parent_doc_ref_id ON doc (parent_doc_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE doc_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES doc (ref_id)
            );
    """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS doc_event""")
    op.execute("""DROP TABLE IF EXISTS doc""")
    op.execute("""DROP TABLE IF EXISTS doc_collection_event""")
    op.execute("""DROP TABLE IF EXISTS doc_collection""")
