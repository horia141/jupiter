"""Add tables for big plan milestones

Revision ID: 846fedf15dd7
Revises: 236220c9ed53
Create Date: 2025-06-12 18:24:28.668509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '846fedf15dd7'
down_revision = '236220c9ed53'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE big_plan_milestone (
            ref_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            archived BOOLEAN NOT NULL,
            archival_reason VARCHAR,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            archived_time DATETIME,
            big_plan_ref_id INTEGER NOT NULL,
            date DATETIME NOT NULL,
            name VARCHAR NOT NULL,
            PRIMARY KEY (ref_id),
            FOREIGN KEY (big_plan_ref_id) REFERENCES big_plan (ref_id)
        );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_big_plan_milestone_big_plan_ref_id ON big_plan_milestone (big_plan_ref_id);
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_big_plan_milestone_big_plan_ref_id_date ON big_plan_milestone (big_plan_ref_id, date);
    """
    )
    op.execute(
        """
        CREATE TABLE big_plan_milestone_event (
            owner_ref_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            session_index INTEGER NOT NULL,
            name VARCHAR(32) NOT NULL,
            source VARCHAR(16) NOT NULL,
            owner_version INTEGER NOT NULL,
            kind VARCHAR(16) NOT NULL,
            data JSON,
            PRIMARY KEY (owner_ref_id, timestamp, session_index, name),
            FOREIGN KEY (owner_ref_id) REFERENCES big_plan_milestone (ref_id)
        );
    """
    )


def downgrade() -> None:
    pass
