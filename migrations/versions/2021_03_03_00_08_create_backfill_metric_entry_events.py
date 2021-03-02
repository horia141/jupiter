"""Create backfill metric entry events


Revision ID: 235dd9ee6fe1
Revises: 646fd1d19041
Create Date: 2021-03-03 00:08:32.429468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '235dd9ee6fe1'
down_revision = '646fd1d19041'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    insert into metric_entry_event (owner_reF_id, timestamp, session_index, name, data)
    select 
        ref_id as owner_ref_id, 
        created_time as timestamp, 
        0 as session_index, 
        'Created' as name, 
        json_object(
            'metric_ref_id', metric_ref_id, 
            'timestamp', created_time, 
            'collection_tine', collection_time, 
            'value', value, 
            'notes', notes) as data 
    from metric_entry 
    where ref_id not in (
        select distinct(ref_id)
        from metric_entry me 
        join metric_entry_event mee 
        on me.ref_id = mee.owner_ref_id 
        and mee.name = 'Created')
    """)


def downgrade():
    pass
