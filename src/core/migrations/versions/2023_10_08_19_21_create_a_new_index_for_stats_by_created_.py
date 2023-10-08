"""Create a new index for stats by created time

Revision ID: 44758da7bd17
Revises: c8ac5dcc06e5
Create Date: 2023-10-08 19:21:12.287346

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "44758da7bd17"
down_revision = "c8ac5dcc06e5"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE INDEX ix_gamification_score_stats_score_log_ref_id_period_created_time ON gamification_score_stats (score_log_ref_id, period, created_time);
    """
    )


def downgrade():
    pass
