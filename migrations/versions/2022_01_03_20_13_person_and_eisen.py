"""Person and eisen

Revision ID: a8d0d5e15770
Revises: 5fe8147f542c
Create Date: 2022-01-03 20:13:47.025674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8d0d5e15770'
down_revision = '5fe8147f542c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        alter table person
        add column catch_up_eisen2""")
    op.execute("""
        update person
        set catch_up_eisen2='regular'
        where catch_up_period is not null and catch_up_eisen2 is null and catch_up_eisen is '[]'""")
    op.execute("""
        create temporary table person_backup (
            ref_id INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            name VARCHAR NOT NULL, 
            relationship VARCHAR NOT NULL, 
            catch_up_project_ref_id INTEGER, 
            catch_up_period VARCHAR, 
            catch_up_eisen VARCHAR, 
            catch_up_difficulty VARCHAR, 
            catch_up_actionable_from_day INTEGER, 
            catch_up_actionable_from_month INTEGER, 
            catch_up_due_at_time VARCHAR, 
            catch_up_due_at_day INTEGER, 
            catch_up_due_at_month INTEGER, 
            birthday VARCHAR,
            PRIMARY KEY (ref_id)
        )
        """)
    op.execute("""
        insert into person_backup
        select
            ref_id, 
            archived, 
            created_time,
            last_modified_time,
            archived_time,
            name,
            relationship,
            catch_up_project_ref_id,
            catch_up_period,
            catch_up_eisen2 AS catch_up_eisen, 
            catch_up_difficulty,
            catch_up_actionable_from_day,
            catch_up_actionable_from_month,
            catch_up_due_at_time,
            catch_up_due_at_day,
            catch_up_due_at_month,
            birthday
        from person
        """)
    op.execute("""
        drop table person
        """)
    op.execute("""
        create table person (
            ref_id INTEGER NOT NULL, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            name VARCHAR NOT NULL, 
            relationship VARCHAR NOT NULL, 
            catch_up_project_ref_id INTEGER, 
            catch_up_period VARCHAR, 
            catch_up_eisen VARCHAR, 
            catch_up_difficulty VARCHAR, 
            catch_up_actionable_from_day INTEGER, 
            catch_up_actionable_from_month INTEGER, 
            catch_up_due_at_time VARCHAR, 
            catch_up_due_at_day INTEGER, 
            catch_up_due_at_month INTEGER, 
            birthday VARCHAR,
            PRIMARY KEY (ref_id)
        )
        """)
    op.execute("""
        insert into person
        select ref_id, 
            archived, 
            created_time,
            last_modified_time,
            archived_time,
            name,
            relationship,
            catch_up_project_ref_id,
            catch_up_period,
            catch_up_eisen, 
            catch_up_difficulty,
            catch_up_actionable_from_day,
            catch_up_actionable_from_month,
            catch_up_due_at_time,
            catch_up_due_at_day,
            catch_up_due_at_month,
            birthday
        from person_backup
        """)
    op.execute("""
        drop table person_backup
        """)


def downgrade() -> None:
    pass
