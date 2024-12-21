"""Create journal tables

Revision ID: accd87afae45
Revises: 2f7390ee2ae2
Create Date: 2024-01-03 00:46:25.182784

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "accd87afae45"
down_revision = "2f7390ee2ae2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE journal_collection (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            periods JSON NOT NULL,
            writing_task_project_ref_id INTEGER NOT NULL,
            writing_task_eisen VARCHAR(16) NOT NULL,
            writing_task_difficulty VARCHAR(8) NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace (ref_id)
            FOREIGN KEY (writing_task_project_ref_id) REFERENCES project (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_journal_collection_workspace_ref_id ON journal_collection (workspace_ref_id);
    """
    )
    op.execute(
        """
        CREATE TABLE journal_collection_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES journal_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE TABLE journal (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            journal_collection_ref_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            source VARCHAR(16) NOT NULL,
            right_now DATE NOT NULL,
            period VARCHAR(16) NOT NULL,
            timeline VARCHAR(16) NOT NULL,
            report JSON NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (journal_collection_ref_id) REFERENCES journal_collection (ref_id)
            );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_journal_journal_collection_ref_id ON journal (journal_collection_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_journal_journal_collection_ref_id_period_timeline ON journal (journal_collection_ref_id, period, timeline);
    """
    )
    op.execute(
        """
        CREATE TABLE journal_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES journal (ref_id)
            );
    """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE IF EXISTS journal_event""")
    op.execute("""DROP TABLE IF EXISTS journal""")
    op.execute("""DROP TABLE IF EXISTS journal_collection_event""")
    op.execute("""DROP TABLE IF EXISTS journal_collection""")
