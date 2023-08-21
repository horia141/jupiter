"""Add gamification scores tables

Revision ID: bf2c22f90e40
Revises: a8268d01e4c1
Create Date: 2023-08-18 12:58:21.836855

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bf2c22f90e40"
down_revision = "a8268d01e4c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Gamification Score Log
    op.execute(
        """
        CREATE TABLE gamification_score_log (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            user_ref_id INTEGER NOT NULL, 
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (user_ref_id) REFERENCES user (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_gamification_score_log_user_ref_id ON gamification_score_log (user_reF_id);"""
    )
    op.execute(
        """
    CREATE TABLE gamification_score_log_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gamification_score_log (ref_id)
    );"""
    )

    # Gamification Score Log Entry

    op.execute(
        """
        CREATE TABLE gamification_score_log_entry (
            ref_id INTEGER NOT NULL, 
            version INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            score_log_ref_id INTEGER NOT NULL,
            source VARCHAR(30) NOT NULL,
            task_ref_id INTEGER NOT NULL,
            difficulty VARCHAR(30) NULL,
            success BOOL NOT NULL,
            score INTEGER NOT NULL,
            PRIMARY KEY (ref_id), 
            FOREIGN KEY (score_log_ref_id) REFERENCES score_log (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_gamification_score_log_entry_score_log_ref_id_source_task_ref_id ON gamification_score_log_entry (score_log_ref_id, source, task_ref_id);"""
    )
    op.execute(
        """
        CREATE INDEX ix_gamification_score_log_entry_score_log_ref_id ON gamification_score_log_entry (score_log_ref_id);"""
    )
    op.execute(
        """
    CREATE TABLE gamification_score_log_entry_event (
        owner_ref_id INTEGER NOT NULL, 
        timestamp DATETIME NOT NULL, 
        session_index INTEGER NOT NULL, 
        name VARCHAR(32) NOT NULL, 
        source VARCHAR(16) NOT NULL, 
        owner_version INTEGER NOT NULL, 
        kind VARCHAR(16) NOT NULL, 
        data JSON, 
        PRIMARY KEY (owner_ref_id, timestamp, session_index, name), 
        FOREIGN KEY (owner_ref_id) REFERENCES gamification_score_log_entry (ref_id)
    );"""
    )

    # Gamification Score Stats

    op.execute(
        """
    CREATE TABLE gamification_score_stats (
        score_log_ref_id INTEGER NOT NULL,
        period VARCHAR(12) NULL,
        timeline VARCHAR(24) NOT NULL,
        total_score INTEGER NOT NULL,
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        FOREIGN KEY (score_log_ref_id) REFERENCES score_log (ref_id)
    );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_gamification_score_stats_score_log_ref_id_period_timeline ON gamification_score_stats (score_log_ref_id, period, timeline);
    """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE gamification_score_log;""")
    op.execute("""DROP TABLE gamification_score_log_event;""")
    op.execute("""DROP TABLE gamification_score_log_entry;""")
    op.execute("""DROP TABLE gamification_score_log_entry_event;""")
    op.execute("""DROP TABLE gamification_score_stats;""")
