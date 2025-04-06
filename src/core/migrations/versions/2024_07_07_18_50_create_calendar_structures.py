"""Create schedule structures

Revision ID: 45fe25fb545d
Revises: 58dae1452d44
Create Date: 2024-07-07 18:50:20.341952

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "45fe25fb545d"
down_revision = "58dae1452d44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE schedule_domain (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_schedule_domain_workspace_ref_id ON schedule_domain (workspace_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_domain_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_stream (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            schedule_domain_ref_id INTEGER NOT NULL,
            source VARCHAR(16) NOT NULL,
            name VARCHAR NOT NULL,
            color VARCHAR(12) NOT NULL,
            source_ical_url VARCHAR,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (schedule_domain_ref_id) REFERENCES schedule_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_schedule_stream_schedule_domain_ref_id ON schedule_stream (schedule_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_stream_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_event_in_day (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            schedule_domain_ref_id INTEGER NOT NULL,
            schedule_stream_ref_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (schedule_domain_ref_id) REFERENCES schedule_domain (ref_id)
            FOREIGN KEY (schedule_stream_ref_id) REFERENCES schedule_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_schedule_event_in_day_schedule_domain_ref_id ON schedule_event_in_day (schedule_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_schedule_event_in_day_schedule_stream_ref_id ON schedule_event_in_day (schedule_stream_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_event_in_day_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_event_in_day (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_event_full_days (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            schedule_domain_ref_id INTEGER NOT NULL,
            schedule_stream_ref_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (schedule_domain_ref_id) REFERENCES schedule_domain (ref_id)
            FOREIGN KEY (schedule_stream_ref_id) REFERENCES schedule_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_schedule_event_full_days_schedule_domain_ref_id ON schedule_event_full_days (schedule_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_schedule_event_full_days_schedule_stream_ref_id ON schedule_event_full_days (schedule_stream_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_event_full_days_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES schedule_event_full_days (ref_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS schedule_event_full_days_event")
    op.execute("DROP TABLE IF EXISTS schedule_event_full_days")
    op.execute("DROP TABLE IF EXISTS schedule_event_in_day_event")
    op.execute("DROP TABLE IF EXISTS schedule_event_in_day")
    op.execute("DROP TABLE IF EXISTS schedule_stream_event")
    op.execute("DROP TABLE IF EXISTS schedule_stream")
    op.execute("DROP TABLE IF EXISTS schedule_domain_event")
    op.execute("DROP TABLE IF EXISTS schedule_domain")
