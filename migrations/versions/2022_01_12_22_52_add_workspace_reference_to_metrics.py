"""Add workspace reference to metrics


Revision ID: 016859689ec3
Revises: a9c77b138685
Create Date: 2022-01-12 22:52:41.021483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016859689ec3'
down_revision = 'a9c77b138685'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TEMPORARY TABLE tmp_metric AS
        SELECT * from metric;
        """)
    op.execute("""
        DROP TABLE metric;
    """)
    op.execute("""
        CREATE TABLE metric (
            ref_id INTEGER NOT NULL,
            version INTEGER,
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            workspace_ref_id INTEGER NOT NULL,
            the_key VARCHAR(64) NOT NULL, 
            name VARCHAR NOT NULL,  
            metric_unit VARCHAR, 
            collection_period VARCHAR,
            collection_project_ref_id INTEGER,
            collection_eisen VARCHAR, 
            collection_difficulty VARCHAR, 
            collection_actionable_from_day INTEGER, 
            collection_actionable_from_month INTEGER, 
            collection_due_at_time VARCHAR, 
            collection_due_at_day INTEGER,
            collection_due_at_month INTEGER, 
            PRIMARY KEY (ref_id)
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace(ref_id)
        );
    """)
    op.execute("""
        INSERT INTO metric (
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            workspace_ref_id,
            the_key, 
            name,  
            metric_unit, 
            collection_period,
            collection_project_ref_id,
            collection_eisen, 
            collection_difficulty, 
            collection_actionable_from_day, 
            collection_actionable_from_month, 
            collection_due_at_time, 
            collection_due_at_day,
            collection_due_at_month
        ) SELECT
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            1 AS workspace_ref_id,
            the_key, 
            name,  
            metric_unit, 
            collection_period,
            collection_project_ref_id,
            collection_eisen, 
            collection_difficulty, 
            collection_actionable_from_day, 
            collection_actionable_from_month, 
            collection_due_at_time, 
            collection_due_at_day,
            collection_due_at_month
        FROM tmp_metric;
    """)
    op.execute("""
        DROP TABLE tmp_metric;
    """)


def downgrade() -> None:
    pass
