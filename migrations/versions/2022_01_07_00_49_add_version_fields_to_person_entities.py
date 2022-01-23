"""Add version fields to person entities

Revision ID: 783ed9de38cf
Revises: c8c90c44a6db
Create Date: 2022-01-07 00:49:46.477462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '783ed9de38cf'
down_revision = 'c8c90c44a6db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
            alter table prm_database add column version INTEGER;
        """)
    op.execute("""
            update prm_database 
            set version=(
                select value from (
                    select 
                        owner_ref_id, 
                        count(*)+1 as value 
                    from prm_database_event 
                    group by owner_ref_id) as foo 
                where prm_database.ref_id=foo.owner_ref_id);
        """)
    op.execute("""
            alter table prm_database_event add column owner_version INTEGER;
        """)
    op.execute("""
            update prm_database_event
             set owner_version=(
                select version from (
                    select 
                        ref, 
                        ts1, 
                        count(*) as version 
                    from (
                        select 
                            bar.owner_ref_id as ref, 
                            bar.timestamp as ts1, 
                            foo.timestamp as ts2 
                        from prm_database_event as bar 
                        join (
                            select 
                                owner_ref_id, 
                                timestamp from 
                            prm_database_event) as foo 
                        on bar.owner_ref_id=foo.owner_ref_id 
                        where ts1 >= ts2) 
                    group by ref, ts1 
                    order by ref, ts1) as baz 
                where 
                    prm_database_event.owner_ref_id=baz.ref
                and prm_database_event.timestamp=baz.ts1);
        """)

    op.execute("""
            alter table person add column version INTEGER;
        """)
    op.execute("""
            update person 
            set version=(
                select value from (
                    select 
                        owner_ref_id, 
                        count(*)+1 as value 
                    from person_event 
                    group by owner_ref_id) as foo 
                where person.ref_id=foo.owner_ref_id);
        """)
    op.execute("""
            alter table person_event add column owner_version INTEGER;
        """)
    op.execute("""
            update person_event
             set owner_version=(
                select version from (
                    select 
                        ref, 
                        ts1, 
                        count(*) as version 
                    from (
                        select 
                            bar.owner_ref_id as ref, 
                            bar.timestamp as ts1, 
                            foo.timestamp as ts2 
                        from person_event as bar 
                        join (
                            select 
                                owner_ref_id, 
                                timestamp from 
                            person_event) as foo 
                        on bar.owner_ref_id=foo.owner_ref_id 
                        where ts1 >= ts2) 
                    group by ref, ts1 
                    order by ref, ts1) as baz 
                where 
                    person_event.owner_ref_id=baz.ref
                and person_event.timestamp=baz.ts1);
        """)


def downgrade() -> None:
    pass
