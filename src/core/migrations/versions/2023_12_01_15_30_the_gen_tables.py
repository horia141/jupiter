"""The gen tables

Revision ID: e743ba3afcea
Revises: 2bec03c27977
Create Date: 2023-12-01 15:30:00.093323

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e743ba3afcea"
down_revision = "2bec03c27977"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE gen_log (
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
        CREATE UNIQUE INDEX ix_gen_log_workspace_ref_id ON gen_log (workspace_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE gen_log_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gen_log (ref_id)
    );"""
    )

    op.execute(
        """
        CREATE TABLE gen_log_entry (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            gen_log_ref_id INTEGER NOT NULL,
            source VARCHAR(30) NOT NULL,
            gen_even_if_not_modified BOOLEAN NOT NULL,
            today DATE NOT NULL,
            gen_targets JSON NOT NULL,
            period JSON,
            filter_project_ref_ids JSON,
            filter_habit_ref_ids JSON,
            filter_chore_ref_ids JSON,
            filter_metric_ref_ids JSON,
            filter_person_ref_ids JSON,
            filter_slack_task_ref_ids JSON,
            filter_email_task_ref_ids JSON,
            opened BOOLEAN NOT NULL,
            entity_created_records JSON NOT NULL,
            entity_updated_records JSON NOT NULL,
            entity_removed_records JSON NOT NULL,
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (gen_log_ref_id) REFERENCES gen_log (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_gen_log_entry_gen_log_ref_id ON gen_log_entry (gen_log_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE gen_log_entry_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gen_log_entry (ref_id)
    );"""
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS gen_log;""")
    op.execute("""DROP TABLE IF EXISTS gen_log_event;""")
    op.execute("""DROP TABLE IF EXISTS gen_log_entry;""")
    op.execute("""DROP TABLE IF EXISTS gen_log_entry_event;""")
