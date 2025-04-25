"""Add structures for stats

Revision ID: baf2d13b02f8
Revises: aec26c6044d3
Create Date: 2025-04-24 20:59:48.712653

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "baf2d13b02f8"
down_revision = "aec26c6044d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE stats_log (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            archival_reason VARCHAR,
            workspace_ref_id INTEGER NOT NULL, 
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_stats_log_workspace_ref_id ON stats_log (workspace_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE stats_log_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES stats_log (ref_id)
    );"""
    )

    op.execute(
        """
        CREATE TABLE stats_log_entry (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            archival_reason VARCHAR,
            stats_log_ref_id INTEGER NOT NULL,
            source VARCHAR(30) NOT NULL,
            name VARCHAR NOT NULL,
            stats_targets JSON NOT NULL,
            today DATE NOT NULL,
            filter_habit_ref_ids JSON,
            filter_big_plan_ref_ids JSON,
            filter_journal_ref_ids JSON,
            entity_records JSON NOT NULL,
            opened BOOLEAN NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (stats_log_ref_id) REFERENCES stats_log (ref_id)
        );"""
    )

    op.execute(
        """
        CREATE INDEX ix_stats_log_entry_stats_log_ref_id ON stats_log_entry (stats_log_ref_id);"""
    )

    op.execute(
        """
        CREATE TABLE stats_log_entry_event (
            owner_ref_id INTEGER NOT NULL, 
            timestamp DATETIME NOT NULL, 
            session_index INTEGER NOT NULL, 
            name VARCHAR(32) NOT NULL, 
            source VARCHAR(16) NOT NULL, 
            owner_version INTEGER NOT NULL, 
            kind VARCHAR(16) NOT NULL, 
            data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES stats_log_entry (ref_id)
    );"""
    )

    op.execute(
        """
        INSERT INTO stats_log
        SELECT
            ref_id as ref_id,
            1 as version,
            0 as archived,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            null as archival_reason,
            ref_id as workspace_ref_id
        FROM workspace;
    """
    )
    op.execute(
        """
        INSERT INTO stats_log_event
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


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS stats_log;""")
    op.execute("""DROP TABLE IF EXISTS stats_log_event;""")
    op.execute("""DROP TABLE IF EXISTS stats_log_entry;""")
    op.execute("""DROP TABLE IF EXISTS stats_log_entry_event;""")
