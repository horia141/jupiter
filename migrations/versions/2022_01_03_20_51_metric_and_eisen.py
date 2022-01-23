"""Metric and eisen

Revision ID: f907cc66856a
Revises: a8d0d5e15770
Create Date: 2022-01-03 20:51:00.343541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f907cc66856a'
down_revision = 'a8d0d5e15770'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
            alter table metric
            add column collection_eisen2""")
    op.execute("""
            update metric
            set collection_eisen2='regular'
            where collection_period is not null and collection_eisen2 is null and collection_eisen is '[]'""")
    op.execute("""
            update metric
            set collection_eisen2='regular'
            where collection_period is not null and collection_eisen2 is null 
            and collection_eisen is '["important"]'""")
    op.execute("""
            create temporary table metric_backup (
                ref_id INTEGER NOT NULL, 
	            archived BOOLEAN NOT NULL, 
	            created_time DATETIME NOT NULL, 
	            last_modified_time DATETIME NOT NULL, 
	            archived_time DATETIME, 
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
            )
            """)
    op.execute("""
            insert into metric_backup
            select
                ref_id,
	            archived,
	            created_time,
	            last_modified_time,
	            archived_time,
	            the_key,
	            name,
	            metric_unit,
	            collection_period,
	            collection_project_ref_id,
	            collection_eisen2 as collection_eisen, 
	            collection_difficulty,
	            collection_actionable_from_day,
	            collection_actionable_from_month,
	            collection_due_at_time,
	            collection_due_at_day,
	            collection_due_at_month
            from metric
            """)
    op.execute("""
            drop table metric
            """)
    op.execute("""
            create table metric (
                ref_id INTEGER NOT NULL, 
	            archived BOOLEAN NOT NULL, 
	            created_time DATETIME NOT NULL, 
	            last_modified_time DATETIME NOT NULL, 
	            archived_time DATETIME, 
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
            )
            """)
    op.execute("""
            insert into metric
            select
                ref_id,
	            archived,
	            created_time,
	            last_modified_time,
	            archived_time,
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
            from metric_backup
            """)
    op.execute("""
            drop table metric_backup
            """)


def downgrade() -> None:
    pass
