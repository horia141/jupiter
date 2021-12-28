"""Backfill PRM Database

Revision ID: 670ea976fe9f
Revises: 0c393dd2ea3c
Create Date: 2021-05-06 16:14:02.348642

"""
from alembic import op
import sqlalchemy as sa

import pendulum


# revision identifiers, used by Alembic.
revision = '670ea976fe9f'
down_revision = '0c393dd2ea3c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    right_now = pendulum.now("UTC")
    op.execute(f"""
            insert into prm_database (ref_id, archived, created_time, last_modified_time, archived_time, catch_up_project_ref_id)
            values (1, False, '{right_now.to_datetime_string()}', '{right_now.to_datetime_string()}', Null, 1)
            """)
    op.execute("""
            insert into prm_database_event (owner_ref_id, timestamp, session_index, name, data)
            select 
                ref_id as owner_ref_id, 
                created_time as timestamp, 
                0 as session_index, 
                'Created' as name, 
                json_object(
                    'timestamp', created_time,
                    'catch_up_project_ref_id', 1) as data 
            from prm_database 
            where ref_id not in (
                select distinct(ref_id)
                from prm_database m
                join prm_database_event me 
                on m.ref_id = me.owner_ref_id 
                and me.name = 'Created')""")


def downgrade() -> None:
    pass
