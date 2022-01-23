"""Add PRM database workspace ref

Revision ID: 21f25eae7b5c
Revises: 31695e3a6ce7
Create Date: 2022-01-12 22:23:40.059778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21f25eae7b5c'
down_revision = '31695e3a6ce7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TEMPORARY TABLE prm_database_tmp AS
        SELECT
            ref_id, 
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            catch_up_project_ref_id,
            version
        FROM prm_database;
    """)
    op.execute("""
        DROP TABLE prm_database;
    """)
    op.execute("""
        CREATE TABLE prm_database (
            ref_id INTEGER NOT NULL,
            version INTEGER, 
            archived BOOLEAN NOT NULL, 
            created_time DATETIME NOT NULL, 
            last_modified_time DATETIME NOT NULL, 
            archived_time DATETIME,
            workspace_ref_id INTEGER NOT NULL,
            catch_up_project_ref_id INTEGER NOT NULL, 
            PRIMARY KEY (ref_id),
            FOREIGN KEY (workspace_ref_id) REFERENCES workspace(ref_id)
        );
    """)
    op.execute("""
        INSERT INTO prm_database (
            ref_id, 
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            workspace_ref_id,
            catch_up_project_ref_id
        ) SELECT 
            ref_id, 
            version,
            archived, 
            created_time, 
            last_modified_time, 
            archived_time, 
            1 as workspace_ref_id, 
            catch_up_project_ref_id
        FROM prm_database_tmp;
    """)
    op.execute("""
        DROP TABLE prm_database_tmp;
    """)


def downgrade() -> None:
    pass
