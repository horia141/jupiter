"""Add the push integration group table

Revision ID: dce7f1f230a8
Revises: 5c7e6a943950
Create Date: 2022-03-18 23:52:47.826747

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "dce7f1f230a8"
down_revision = "5c7e6a943950"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    CREATE TABLE push_integration_group (
        ref_id INTEGER NOT NULL, 
        version INTEGER NOT NULL, 
        archived BOOLEAN NOT NULL, 
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        archived_time DATETIME, 
        workspace_ref_id INTEGER NOT NULL, 
        PRIMARY KEY (ref_id), 
        FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
    );"""
    )
    op.execute(
        """
    CREATE UNIQUE INDEX ix_push_integration_group_workspace_ref_id ON push_integration_group (workspace_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE push_integration_group_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY(owner_ref_id) REFERENCES push_integration_group (ref_id)
    );"""
    )


def downgrade() -> None:
    op.execute("""DROP TABLE push_integration_group_event""")
    op.execute("""DROP TABLE push_integration_group""")
