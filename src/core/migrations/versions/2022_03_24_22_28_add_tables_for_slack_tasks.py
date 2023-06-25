"""Add tables for slack tasks

Revision ID: 699090c0908a
Revises: dce7f1f230a8
Create Date: 2022-03-24 22:28:09.040864

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "699090c0908a"
down_revision = "dce7f1f230a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE slack_task_collection (
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
        CREATE UNIQUE INDEX ix_slack_task_collection_push_integration_group_ref_id ON slack_task_collection (push_integration_group_ref_id);"""
    )
    op.execute(
        """
        CREATE TABLE slack_task_collection_event (
            owner_ref_id INTEGER NOT NULL, 
            timestamp DATETIME NOT NULL, 
            session_index INTEGER NOT NULL, 
            name VARCHAR(32) NOT NULL, 
            source VARCHAR(16) NOT NULL, 
            owner_version INTEGER NOT NULL, 
            kind VARCHAR(16) NOT NULL, 
            data JSON, 
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
            FOREIGN KEY(owner_ref_id) REFERENCES slack_task_collection (ref_id)
        );"""
    )
    op.execute(
        """
        CREATE TABLE slack_task (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            slack_task_collection_ref_id INTEGER NOT NULL, 
            user VARCHAR NOT NULL,
            channel VARCHAR NOT NULL,
            message VARCHAR NULL,
            generation_extra_info VARCHAR NULL,
            has_generated_task BOOLEAN NOT NULL,
            CONSTRAINT pk_slack_task PRIMARY KEY (ref_id), 
            CONSTRAINT fk_slack_task_slack_task_collection_ref_id_slack_task_collection FOREIGN KEY(slack_task_collection_ref_id) REFERENCES slack_task_collection (ref_id)
        );"""
    )
    op.execute(
        """
        CREATE INDEX ix_slack_task_slack_task_collection_ref_id ON slack_task (slack_task_collection_ref_id);"""
    )
    op.execute(
        """
        CREATE TABLE slack_task_event (
            owner_ref_id INTEGER NOT NULL, 
            timestamp DATETIME NOT NULL, 
            session_index INTEGER NOT NULL, 
            name VARCHAR(32) NOT NULL, 
            source VARCHAR(16) NOT NULL, 
            owner_version INTEGER NOT NULL, 
            kind VARCHAR(16) NOT NULL, 
            data JSON, 
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
            FOREIGN KEY(owner_ref_id) REFERENCES slack_task (ref_id)
        );"""
    )


def downgrade() -> None:
    op.execute("""DROP TABLE slack_task_event""")
    op.execute("""DROP TABLE slack_task""")
    op.execute("""DROP TABLE slack_task_collection_event""")
    op.execute("""DROP TABLE slack_task_collection""")
