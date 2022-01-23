"""Add person PRM database ref


Revision ID: a9c77b138685
Revises: 21f25eae7b5c
Create Date: 2022-01-12 22:38:21.513794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9c77b138685'
down_revision = '21f25eae7b5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TEMPORARY TABLE tmp_person AS
        SELECT * from person;
    """)
    op.execute("""
        DROP TABLE person;
    """)
    op.execute("""
        CREATE TABLE person (
            ref_id INTEGER NOT NULL, 
            version INTEGER,
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME, 
            prm_database_ref_id INTEGER NOT NULL,
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
            PRIMARY KEY (ref_id),
            FOREIGN KEY (prm_database_ref_id) REFERENCES prm_database(ref_id)
        );
    """)
    op.execute("""
        INSERT INTO person (
            ref_id, 
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            prm_database_ref_id,
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
        ) SELECT   
            ref_id, 
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            1 as prm_database_ref_id,
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
        FROM tmp_person;
    """)
    op.execute("""
        DROP TABLE tmp_person;
    """)


def downgrade() -> None:
    pass
