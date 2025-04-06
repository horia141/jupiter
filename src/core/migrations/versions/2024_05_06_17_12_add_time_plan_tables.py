"""Add time plan tables

Revision ID: eb965cd038e5
Revises: 6dd9a9a34fa8
Create Date: 2024-05-06 17:12:38.384423

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "eb965cd038e5"
down_revision = "6dd9a9a34fa8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE time_plan_domain (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            days_until_gc INTEGER NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_time_plan_domain_workspace_ref_id ON time_plan_domain (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE time_plan_domain_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_plan_domain (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE TABLE time_plan (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            time_plan_domain_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            source VARCHAR(16) NOT NULL,
            right_now DATE NOT NULL,
            period VARCHAR(16) NOT NULL,
            timeline VARCHAR(16) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (time_plan_domain_ref_id) REFERENCES time_plan_domain (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_time_plan_time_plan_domain_ref_id ON time_plan (time_plan_domain_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_time_plan_time_plan_domain_ref_id_right_now ON time_plan (time_plan_domain_ref_id, right_now)
        WHERE archived=0;
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_time_plan_time_plan_domain_ref_id_period_timeline ON time_plan (time_plan_domain_ref_id, period, timeline)
        WHERE archived=0;
    """
    )
    op.execute(
        """
        CREATE TABLE time_plan_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_plan (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE TABLE time_plan_activity (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            time_plan_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            target VARCHAR(16) NOT NULL,
            target_ref_id INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            feasability VARCHAR(16) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (time_plan_ref_id) REFERENCES time_plan (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_time_plan_activity_time_plan_ref_id ON time_plan_activity (time_plan_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_time_plan_activity_time_plan_ref_id_target_target_ref_id ON time_plan_activity (time_plan_ref_id, target, target_ref_id)
        WHERE archived=0;
    """
    )
    op.execute(
        """
        CREATE TABLE time_plan_activity_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_plan_activity (ref_id)
            );
    """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS time_plan_activity_event""")
    op.execute("""DROP TABLE IF EXISTS time_plan_activity""")
    op.execute("""DROP TABLE IF EXISTS time_plan_event""")
    op.execute("""DROP TABLE IF EXISTS time_plan""")
    op.execute("""DROP TABLE IF EXISTS time_plan_domain_event""")
    op.execute("""DROP TABLE IF EXISTS time_plan_domain""")
