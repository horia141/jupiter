"""Add all the user and auth tables

Revision ID: 039c2afe8bcb
Revises: bb9cf0028fc1
Create Date: 2023-06-01 14:43:50.093640

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "039c2afe8bcb"
down_revision = "bb9cf0028fc1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE user (
        ref_id INTEGER NOT NULL, 
        version INTEGER NOT NULL, 
        archived BOOLEAN NOT NULL, 
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        archived_time DATETIME, 
        email_address STRING NOT NULL UNIQUE ,
        name STRING NOT NULL,
        timezone STRING NOT NULL,
        PRIMARY KEY (ref_id)
        );
        """
    )
    op.execute(
        """
            CREATE UNIQUE INDEX ix_user_email_address ON user (email_address);
    """
    )
    op.execute(
        """
        CREATE TABLE user_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY(owner_ref_id) REFERENCES user (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE TABLE auth (
        ref_id INTEGER NOT NULL, 
        version INTEGER NOT NULL, 
        archived BOOLEAN NOT NULL, 
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        archived_time DATETIME, 
        user_ref_id INTEGER NOT NULL UNIQUE,
        password_hash STRING NOT NULL,
        recovery_token_hash STRING NOT NULL,
        PRIMARY KEY (ref_id),
        FOREIGN KEY(user_ref_id) REFERENCES user (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_auth_user_ref_id ON auth (user_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE auth_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY(owner_ref_id) REFERENCES auth (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE TABLE user_workspace_link (
            ref_id INTEGER NOT NULL, 
        version INTEGER NOT NULL, 
        archived BOOLEAN NOT NULL, 
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        archived_time DATETIME, 
        user_ref_id INTEGER NOT NULL UNIQUE,
        workspace_ref_id INTEGER NOT NULL UNIQUE,
        PRIMARY KEY (ref_id),
        FOREIGN KEY (user_ref_id) REFERENCES user (ref_id),
        FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_user_workspace_link_user_ref_id ON user_workspace_link (user_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_user_workspace_link_workspace_ref_id ON user_workspace_link (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE user_workspace_link_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY(owner_ref_id) REFERENCES user_workspace_link (ref_id)
        );
    """
    )


def downgrade():
    op.execute("""DROP TABLE IF EXISTS user_workspace_link_event""")
    op.execute("""DROP TABLE IF EXISTS user_workspace_link""")
    op.execute("""DROP TABLE IF EXISTS auth_event""")
    op.execute("""DROP TABLE IF EXISTS auth""")
    op.execute("""DROP TABLE IF EXISTS user_event""")
    op.execute("""DROP TABLE IF EXISTS user""")
