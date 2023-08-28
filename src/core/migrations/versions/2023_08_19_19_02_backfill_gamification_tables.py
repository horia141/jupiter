"""Backfill gamification tables

Revision ID: 20c0c83a38a8
Revises: bf2c22f90e40
Create Date: 2023-08-19 19:02:54.581550

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "20c0c83a38a8"
down_revision = "bf2c22f90e40"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO gamification_score_log
        SELECT
            ref_id as ref_id,
            1 as version,
            0 as archived,
            created_time as created_time,
            created_time as last_modified_time,
            null as archived_time,
            ref_id as user_ref_id
        FROM user;
    """
    )
    op.execute(
        """
        INSERT INTO gamification_score_log_event
        SELECT
            ref_id as owner_ref_id,
            created_time as timestamp,
            0 as session_index,
            'Created' as name,
            'CLI' as source,
            1 as owner_version,
            'Created' as kind,
            '{}}' as data
        FROM user;
    """
    )


def downgrade():
    pass
