"""Create calendar structures

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
        CREATE TABLE calendar_domain (
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
        CREATE UNIQUE INDEX ix_calendar_domain_workspace_ref_id ON calendar_domain (workspace_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_domain_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES calendar_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_stream (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            calendar_domain_ref_id INTEGER NOT NULL,
            source VARCHAR(16) NOT NULL,
            name VARCHAR NOT NULL,
            color VARCHAR(12) NOT NULL,
            source_ical_url VARCHAR,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (calendar_domain_ref_id) REFERENCES calendar_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_calendar_stream_calendar_domain_ref_id ON calendar_stream (calendar_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_stream_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES calendar_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_event_in_day (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            calendar_domain_ref_id INTEGER NOT NULL,
            calendar_stream_ref_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (calendar_domain_ref_id) REFERENCES calendar_domain (ref_id)
            FOREIGN KEY (calendar_stream_ref_id) REFERENCES calendar_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_calendar_event_in_day_calendar_domain_ref_id ON calendar_event_in_day (calendar_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_calendar_event_in_day_calendar_stream_ref_id ON calendar_event_in_day (calendar_stream_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_event_in_day_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES calendar_event_in_day (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_event_full_days (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            calendar_domain_ref_id INTEGER NOT NULL,
            calendar_stream_ref_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (calendar_domain_ref_id) REFERENCES calendar_domain (ref_id)
            FOREIGN KEY (calendar_stream_ref_id) REFERENCES calendar_stream (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_calendar_event_full_days_calendar_domain_ref_id ON calendar_event_full_days (calendar_domain_ref_id)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_calendar_event_full_days_calendar_stream_ref_id ON calendar_event_full_days (calendar_stream_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE calendar_event_full_days_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES calendar_event_full_days (ref_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS calendar_event_full_days_event")
    op.execute("DROP TABLE IF EXISTS calendar_event_full_days")
    op.execute("DROP TABLE IF EXISTS calendar_event_in_day_event")
    op.execute("DROP TABLE IF EXISTS calendar_event_in_day")
    op.execute("DROP TABLE IF EXISTS calendar_stream_event")
    op.execute("DROP TABLE IF EXISTS calendar_stream")
    op.execute("DROP TABLE IF EXISTS calendar_domain_event")
    op.execute("DROP TABLE IF EXISTS calendar_domain")
