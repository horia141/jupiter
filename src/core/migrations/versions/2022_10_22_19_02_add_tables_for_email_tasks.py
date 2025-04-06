"""Add tables for email tasks

Revision ID: 2e90eb234797
Revises: 8762c5103041
Create Date: 2022-10-22 19:02:37.444118

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2e90eb234797"
down_revision = "8762c5103041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE email_task_collection (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            push_integration_group_ref_id INTEGER NOT NULL, 
            generation_project_ref_id INTEGER NOT NULL,
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (push_integration_group_ref_id) REFERENCES push_integration_group (ref_id),
            FOREIGN KEY (generation_project_ref_id) REFERENCES project (ref_id)
        );"""
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_email_task_collection_push_integration_group_ref_id ON email_task_collection (push_integration_group_ref_id);"""
    )
    op.execute(
        """
        CREATE TABLE email_task_collection_event (
            owner_ref_id INTEGER NOT NULL, 
            timestamp DATETIME NOT NULL, 
            session_index INTEGER NOT NULL, 
            name VARCHAR(32) NOT NULL, 
            source VARCHAR(16) NOT NULL, 
            owner_version INTEGER NOT NULL, 
            kind VARCHAR(16) NOT NULL, 
            data JSON, 
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
            FOREIGN KEY(owner_ref_id) REFERENCES email_task_collection (ref_id)
        );"""
    )
    op.execute(
        """
        CREATE TABLE email_task (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            email_task_collection_ref_id INTEGER NOT NULL, 
            from_address VARCHAR NOT NULL,
            from_name VARCHAR NOT NULL,
            to_address VARCHAR NOT NULL,
            subject VARCHAR NOT NULL,
            body VARCHAR NOT NULL,
            generation_extra_info VARCHAR NULL,
            has_generated_task BOOLEAN NOT NULL,
            CONSTRAINT pk_email_task PRIMARY KEY (ref_id), 
            CONSTRAINT fk_email_task_email_task_collection_ref_id_email_task_collection FOREIGN KEY(email_task_collection_ref_id) REFERENCES email_task_collection (ref_id)
        );"""
    )
    op.execute(
        """
        CREATE INDEX ix_email_task_email_task_collection_ref_id ON email_task (email_task_collection_ref_id);"""
    )
    op.execute(
        """
        CREATE TABLE email_task_event (
            owner_ref_id INTEGER NOT NULL, 
            timestamp DATETIME NOT NULL, 
            session_index INTEGER NOT NULL, 
            name VARCHAR(32) NOT NULL, 
            source VARCHAR(16) NOT NULL, 
            owner_version INTEGER NOT NULL, 
            kind VARCHAR(16) NOT NULL, 
            data JSON, 
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
            FOREIGN KEY(owner_ref_id) REFERENCES email_task (ref_id)
        );"""
    )


def downgrade() -> None:
    op.execute("""DROP TABLE email_task_event""")
    op.execute("""DROP TABLE email_task""")
    op.execute("""DROP TABLE email_task_collection_event""")
    op.execute("""DROP TABLE email_task_collection""")
