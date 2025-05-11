"""Add structures for home config

Revision ID: 20190c88fbc1
Revises: 2f3cd88ada12
Create Date: 2025-05-02 23:01:37.157666

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20190c88fbc1"
down_revision = "2f3cd88ada12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE home_config (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            archival_reason VARCHAR,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            key_habits JSON NOT NULL,
            key_metrics JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_home_config_workspace_ref_id ON home_config (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE home_config_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES home_config (ref_id)
        );
    """
    )

    op.execute(
        """
        INSERT INTO home_config (
            ref_id,
            version,
            archived,
            archival_reason,
            created_time,
            last_modified_time,
            archived_time,
            workspace_ref_id,
            key_habits,
            key_metrics
        )
        SELECT
            ref_id,
            1 as version,
            0 as archived,
            null as archival_reason,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            workspace_ref_id as workspace_ref_id,
            '[]' as key_habits,
            '[]' as key_metrics
        FROM (
            SELECT
                ref_id,
                ref_id as workspace_ref_id,
                created_time as created_time
            FROM workspace
        );
    """
    )
    op.execute(
        """
        INSERT INTO home_config_event
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
              hc.ref_id as ref_id,
              hc.ref_id as home_config_ref_id,
              w.created_time as created_time
            FROM workspace w 
            JOIN home_config hc
            ON w.ref_id=hc.workspace_ref_id
        );
    """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE home_config;
    """
    )
    op.execute(
        """
        DROP TABLE home_config_event;
    """
    )
