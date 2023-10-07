"""Add inbox task and big plan cnt to score stats best

Revision ID: c8ac5dcc06e5
Revises: 1b78d1ca755a
Create Date: 2023-10-07 23:47:44.507280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8ac5dcc06e5'
down_revision = '1b78d1ca755a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE TABLE _gamification_score_period_best (
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
    op.execute("""
        INSERT INTO _gamification_score_period_best
        SELECT
            score_log_ref_id,
            period,
            timeline,
            sub_period,
            total_score,
            created_time,
            last_modified_time
        FROM gamification_score_period_best;
    """)
    op.execute("""DROP TABLE gamification_score_period_best;""")
    op.execute(
        """
    CREATE TABLE gamification_score_period_best (
        score_log_ref_id INTEGER NOT NULL,
        period VARCHAR(12) NULL,
        timeline VARCHAR(24) NOT NULL,
        sub_period VARCHAR(12) NOT NULL,
        total_score INTEGER NOT NULL,
        inbox_task_cnt INTEGER NOT NULL,
        big_plan_cnt INTEGER NOT NULL,
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
    op.execute("""
        INSERT INTO gamification_score_period_best
        SELECT score_log_ref_id,
               period,
               sub_period,
               timeline,
               total_score,
               0,
               0,
               created_time,
               last_modified_time
        FROM _gamification_score_period_best;
    """)


def downgrade():
    with op.batch_alter_table("gamification_score_period_best") as batch_op:
        batch_op.drop_column("inbox_task_cnt")
        batch_op.drop_column("big_plan_cnt")
