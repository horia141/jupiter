"""Add version fields to metrics entities

Revision ID: c8c90c44a6db
Revises: f907cc66856a
Create Date: 2022-01-07 00:15:27.166459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8c90c44a6db'
down_revision = 'f907cc66856a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        alter table metric add column version INTEGER;
    """)
    op.execute("""
        update metric 
        set version=(
            select value from (
                select 
                    owner_ref_id, 
                    count(*)+1 as value 
                from metric_event 
                group by owner_ref_id) as foo 
            where metric.ref_id=foo.owner_ref_id);
    """)
    op.execute("""
        alter table metric_event add column owner_version INTEGER;
    """)
    op.execute("""
        update metric_event
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
                    from metric_event as bar 
                    join (
                        select 
                            owner_ref_id, 
                            timestamp from 
                        metric_event) as foo 
                    on bar.owner_ref_id=foo.owner_ref_id 
                    where ts1 >= ts2) 
                group by ref, ts1 
                order by ref, ts1) as baz 
            where 
                metric_event.owner_ref_id=baz.ref
            and metric_event.timestamp=baz.ts1);
    """)

    op.execute("""
            alter table metric_entry add column version INTEGER;
        """)
    op.execute("""
            update metric_entry 
            set version=(
                select value from (
                    select 
                        owner_ref_id, 
                        count(*)+1 as value 
                    from metric_entry_event 
                    group by owner_ref_id) as foo 
                where metric_entry.ref_id=foo.owner_ref_id);
        """)
    op.execute("""
            alter table metric_entry_event add column owner_version INTEGER;
        """)
    op.execute("""
            update metric_entry_event
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
                        from metric_entry_event as bar 
                        join (
                            select 
                                owner_ref_id, 
                                timestamp from 
                            metric_entry_event) as foo 
                        on bar.owner_ref_id=foo.owner_ref_id 
                        where ts1 >= ts2) 
                    group by ref, ts1 
                    order by ref, ts1) as baz 
                where 
                    metric_entry_event.owner_ref_id=baz.ref
                and metric_entry_event.timestamp=baz.ts1);
        """)


def downgrade() -> None:
    pass
