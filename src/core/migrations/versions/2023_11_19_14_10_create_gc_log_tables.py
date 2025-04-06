"""Create GC log tables

Revision ID: 4638d68a087a
Revises: 9d154be8e4c1
Create Date: 2023-11-19 14:10:12.993018

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "4638d68a087a"
down_revision = "9d154be8e4c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE gc_log (
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
        CREATE UNIQUE INDEX ix_gc_log_workspace_ref_id ON gc_log (workspace_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE gc_log_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gc_log (ref_id)
    );"""
    )

    op.execute(
        """
        CREATE TABLE gc_log_entry (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            gc_log_ref_id INTEGER NOT NULL,
            source VARCHAR(30) NOT NULL,
            gc_targets JSON NOT NULL,
            opened BOOLEAN NOT NULL,
            entity_records JSON NOT NULL,
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (gc_log_ref_id) REFERENCES gc_log (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_gc_log_entry_gc_log_ref_id ON gc_log_entry (gc_log_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE gc_log_entry_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gc_log_entry (ref_id)
    );"""
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS gc_log;""")
    op.execute("""DROP TABLE IF EXISTS gc_log_event;""")
    op.execute("""DROP TABLE IF EXISTS gc_log_entry;""")
    op.execute("""DROP TABLE IF EXISTS gc_log_entry_event;""")
