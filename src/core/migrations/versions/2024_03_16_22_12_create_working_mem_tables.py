"""Create working mem tables

Revision ID: 5c9c383c4f89
Revises: cc1a2f1e3d35
Create Date: 2024-03-16 22:12:32.444182

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5c9c383c4f89"
down_revision = "cc1a2f1e3d35"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE working_mem_collection (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            generation_period VARCHAR(16) NOT NULL,
            cleanup_project_ref_id INTEGER NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
            FOREIGN KEY (cleanup_project_ref_id) REFERENCES project (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_working_mem_collection_workspace_ref_id ON working_mem_collection (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE working_mem_collection_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES working_mem_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE TABLE working_mem (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            working_mem_collection_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            right_now DATE NOT NULL,
            period VARCHAR(16) NOT NULL,
            timeline VARCHAR(16) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (working_mem_collection_ref_id) REFERENCES working_mem_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_working_mem_working_mem_collection_ref_id ON working_mem (working_mem_collection_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_working_mem_working_mem_collection_ref_id_period_timeline ON working_mem (working_mem_collection_ref_id, period, timeline);
    """
    )
    op.execute(
        """
        CREATE TABLE working_mem_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES working_mem (ref_id)
            );
    """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS working_mem_event""")
    op.execute("""DROP TABLE IF EXISTS working_mem""")
    op.execute("""DROP TABLE IF EXISTS working_mem_collection_event""")
    op.execute("""DROP TABLE IF EXISTS working_mem_collection""")
