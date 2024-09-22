"""Add tables for sync log entries

Revision ID: fbf223b452c4
Revises: b91f4501b574
Create Date: 2024-09-16 00:14:10.861571

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "fbf223b452c4"
down_revision = "b91f4501b574"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE schedule_external_sync_log (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            schedule_domain_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (schedule_domain_ref_id) REFERENCES schedule_domain (ref_id)
        );
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_schedule_external_sync_log_schedule_domain_ref_id ON schedule_external_sync_log (schedule_domain_ref_id);
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_external_sync_log_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_external_sync_log (ref_id)
        );
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_external_sync_log_entry (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            schedule_external_sync_log_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            source VARCHAR(16) NOT NULL,
            filter_schedule_stream_ref_id JSON,
            opened BOOLEAN NOT NULL,
            per_stream_results JSON NOT NULL,
            entity_records JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (schedule_external_sync_log_ref_id) REFERENCES schedule_external_sync_log (ref_id)
        );
        """
    )
    op.execute(
        """
            CREATE INDEX ix_schedule_external_sync_log_entry_schedule_external_sync_log_ref_id ON schedule_external_sync_log_entry (schedule_external_sync_log_ref_id);
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_external_sync_log_entry_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_external_sync_log_entry (ref_id)
        );
        """
    )
    op.execute(
        """
        INSERT INTO schedule_external_sync_log
        SELECT
            ref_id as ref_id,
            1 as version,
            0 as archived,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            schedule_domain_ref_id as schedule_domain_ref_id,
            'not_used' as name
        FROM (
            SELECT
              sd.ref_id as ref_id,
              sd.ref_id as schedule_domain_ref_id,
              w.created_time as created_time
            FROM workspace w 
            JOIN schedule_domain sd
            ON w.ref_id=sd.workspace_ref_id
        );
        """
    )
    op.execute(
        """
        INSERT INTO schedule_external_sync_log_event
        SELECT
            ref_id as owner_ref_id,
            created_time as timestamp,
            0 as session_index,
            'Created' as name,
            'CLI' as source,
            1 as owner_version,
            'Created' as kind,
            '{}}' as data
        FROM (
            SELECT
              sd.ref_id as ref_id,
              sd.ref_id as schedule_domain_ref_id,
              w.created_time as created_time
            FROM workspace w 
            JOIN schedule_domain sd
            ON w.ref_id=sd.workspace_ref_id
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE schedule_external_sync_log_entry_event;
        """
    )
    op.execute(
        """
        DROP TABLE schedule_external_sync_log_entry;
        """
    )
    op.execute(
        """
        DROP TABLE schedule_external_sync_log_event;
        """
    )
    op.execute(
        """
        DROP TABLE schedule_external_sync_log;
        """
    )
