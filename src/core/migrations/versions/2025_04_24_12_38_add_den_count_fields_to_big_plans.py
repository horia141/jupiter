"""Add den count fields to big plans

Revision ID: aec26c6044d3
Revises: 4487471c6629
Create Date: 2025-04-24 12:38:38.730346

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "aec26c6044d3"
down_revision = "4487471c6629"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE big_plan_stats (
            big_plan_ref_id INTEGER NOT NULL,
            all_inbox_tasks_cnt INTEGER NOT NULL,
            completed_inbox_tasks_cnt INTEGER NOT NULL,
            created_time DATETIME NOT NULL,
            last_modified_time DATETIME NOT NULL,
            FOREIGN KEY (big_plan_ref_id) REFERENCES big_plan (ref_id),
            UNIQUE (big_plan_ref_id)
        );
        """
    )

    op.execute(
        """
        INSERT INTO big_plan_stats
        SELECT
            ref_id as big_plan_ref_id,
            0 as all_inbox_tasks_cnt,
            0 as completed_inbox_tasks_cnt, 
            created_time as created_time,
            created_time as last_modified_time
        FROM big_plan;
        """
    )


def downgrade() -> None:
    op.execute("""DROP TABLE big_plan_stats;""")
