"""Add period best table

Revision ID: 5d2f27e102f8
Revises: 6cfc8bf6afac
Create Date: 2023-09-03 17:55:59.956247

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5d2f27e102f8"
down_revision = "6cfc8bf6afac"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE TABLE gamification_score_period_best (
        score_log_ref_id INTEGER NOT NULL,
        period VARCHAR(12) NULL,
        timeline VARCHAR(24) NOT NULL,
        sub_period VARCHAR(12) NOT NULL,
        total_score INTEGER NOT NULL,
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        FOREIGN KEY (score_log_ref_id) REFERENCES gamification_score_log (ref_id)
    );
    """
    )
    op.execute(
        """
        CREATE INDEX ix_gamification_score_period_best_score_log_ref_id_period_timeline_sub_period ON gamification_score_period_best (score_log_ref_id, period, timeline, sub_period);
    """
    )


def downgrade():
    op.execute("""DROP TABLE gamification_score_period_best;""")
