"""Add fields for home config

Revision ID: 236220c9ed53
Revises: 625fd14020f4
Create Date: 2025-05-09 21:10:02.610540

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "236220c9ed53"
down_revision = "625fd14020f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DROP INDEX ix_home_config_event_owner_ref_id;
    """
    )

    with op.batch_alter_table("home_config") as batch_op:
        batch_op.add_column(sa.Column("order_of_tabs", sa.JSON))

    op.execute(
        """
        UPDATE home_config SET order_of_tabs = '{"big-screen": [], "small-screen": []}' where order_of_tabs is NULL
    """
    )

    op.execute(
        """
        CREATE TABLE home_tab (
            ref_id INTEGER NOT NULL PRIMARY KEY,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            archival_reason VARCHAR,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            home_config_ref_id INTEGER NOT NULL,
            target VARCHAR(32) NOT NULL,
            name VARCHAR(256) NOT NULL,
            icon VARCHAR(64),
            widget_placement JSON NOT NULL,
            FOREIGN KEY (home_config_ref_id) REFERENCES home_config (ref_id)
        )
    """
    )
    op.execute(
        """
        CREATE INDEX ix_home_tab_home_config_ref_id ON home_tab (home_config_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE home_tab_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES home_tab (ref_id)
        );
    """
    )

    op.execute(
        """
        CREATE TABLE home_widget (
            ref_id INTEGER NOT NULL PRIMARY KEY,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            archival_reason VARCHAR,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            home_tab_ref_id INTEGER NOT NULL,
            name VARCHAR(256) NOT NULL,
            the_type VARCHAR(32) NOT NULL,
            geometry JSON NOT NULL,
            FOREIGN KEY (home_tab_ref_id) REFERENCES home_tab (ref_id)
        )
    """
    )
    op.execute(
        """
        CREATE INDEX ix_home_widget_home_tab_ref_id ON home_widget (home_tab_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE home_widget_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES home_widget (ref_id)
        );
    """
    )


def downgrade() -> None:
    op.execute("DROP TABLE home_tab")
    op.execute("DROP TABLE home_tab_event")
    op.execute("DROP TABLE home_widget")
    op.execute("DROP TABLE home_widget_event")
