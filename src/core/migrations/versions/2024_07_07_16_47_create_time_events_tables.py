"""Create time events tables

Revision ID: 5b937ac5ad07
Revises: 94535a7e2a28
Create Date: 2024-07-07 16:47:03.698448

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "5b937ac5ad07"
down_revision = "94535a7e2a28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE time_event_domain (
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
        CREATE UNIQUE INDEX ix_time_event_domain_workspace_ref_id ON time_event_domain (workspace_ref_id)
        """
    )
    op.execute(
        """
        CREATE TABLE time_event_domain_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_event_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE time_event_in_day_block (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            time_event_domain_ref_id INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            namespace VARCHAR(32) NOT NULL,
            source_entity_ref_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            start_time_in_day VARCHAR(5) NOT NULL,
            duration_mins INTEGER NOT NULL,
            timezone VARCHAR(32) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (time_event_domain_ref_id) REFERENCES time_event_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_time_event_in_day_block_time_event_domain_ref_id ON time_event_in_day_block (time_event_domain_ref_id)
        """
    )
    op.execute(
        """
            CREATE INDEX ix_time_event_in_day_block_namespace_source_entity_ref_id ON time_event_in_day_block (namespace, source_entity_ref_id)
        """
    )
    op.execute(
        """
            CREATE INDEX ix_time_event_in_day_block_time_event_domain_ref_id_start_date ON time_event_in_day_block (time_event_domain_ref_id, start_date)
        """
    )
    op.execute(
        """
        CREATE TABLE time_event_in_day_block_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_event_in_day_block (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE time_event_full_days_block (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            time_event_domain_ref_id INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            namespace VARCHAR(32) NOT NULL,
            source_entity_ref_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            duration_days INTEGER NOT NULL,
            end_date DATE NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (time_event_domain_ref_id) REFERENCES time_event_domain (ref_id)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX ix_time_event_full_days_block_time_event_domain_ref_id ON time_event_full_days_block (time_event_domain_ref_id)
        """
    )
    op.execute(
        """
            CREATE INDEX ix_time_event_full_days_block_namespace_source_entity_ref_id ON time_event_full_days_block (namespace, source_entity_ref_id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_time_event_full_days_block_time_event_domain_ref_id_start_date ON time_event_full_days_block (time_event_domain_ref_id, start_date)
    """
    )
    op.execute(
        """
        CREATE INDEX ix_time_event_full_days_block_time_event_domain_ref_id_end_date ON time_event_full_days_block (time_event_domain_ref_id, end_date)
    """
    )
    op.execute(
        """
        CREATE TABLE time_event_full_days_block_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES time_event_full_days_block (ref_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE time_event_full_days_block_event""")
    op.execute("""DROP TABLE time_event_full_days_block""")
    op.execute("""DROP TABLE time_event_in_day_block_event""")
    op.execute("""DROP TABLE time_event_in_day_block""")
    op.execute("""DROP TABLE time_event_domain_event""")
    op.execute("""DROP TABLE time_event_domain""")
