"""Add inbox task and big plan cnt to score stats

Revision ID: 1b78d1ca755a
Revises: 5d2f27e102f8
Create Date: 2023-10-07 23:20:41.429944

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1b78d1ca755a"
down_revision = "5d2f27e102f8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE TABLE _gamification_score_stats (
        score_log_ref_id INTEGER NOT NULL,
        period VARCHAR(12) NULL,
        timeline VARCHAR(24) NOT NULL,
        total_score INTEGER NOT NULL,
        created_time DATETIME NOT NULL, 
        last_modified_time DATETIME NOT NULL, 
        FOREIGN KEY (score_log_ref_id) REFERENCES gamification_score_log (ref_id)
    );
    """
    )
    op.execute(
        """
        INSERT INTO _gamification_score_stats
        SELECT
            score_log_ref_id,
            period,
            timeline,
            total_score,
            created_time,
            last_modified_time
        FROM gamification_score_stats;
    """
    )
    op.execute("""DROP TABLE gamification_score_stats;""")
    op.execute(
        """
    CREATE TABLE gamification_score_stats (
        score_log_ref_id INTEGER NOT NULL,
        period VARCHAR(12) NULL,
        timeline VARCHAR(24) NOT NULL,
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
        CREATE INDEX ix_gamification_score_stats_score_log_ref_id_period_timeline ON gamification_score_stats (score_log_ref_id, period, timeline);
    """
    )
    op.execute(
        """
        INSERT INTO gamification_score_stats
        SELECT score_log_ref_id,
               period,
               timeline,
               total_score,
               0,
               0,
               created_time,
               last_modified_time
        FROM _gamification_score_stats;
    """
    )
    op.execute("DROP TABLE _gamification_score_stats")


def downgrade():
    with op.batch_alter_table("gamification_score_stats") as batch_op:
        batch_op.drop_column("inbox_task_cnt")
        batch_op.drop_column("big_plan_cnt")
