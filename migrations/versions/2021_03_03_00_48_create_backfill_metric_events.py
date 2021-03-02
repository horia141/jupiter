"""Create backfill metric events

Revision ID: ce847ba7aebe
Revises: 235dd9ee6fe1
Create Date: 2021-03-03 00:48:14.454453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce847ba7aebe'
down_revision = '235dd9ee6fe1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        insert into metric_event (owner_reF_id, timestamp, session_index, name, data)
        select 
            ref_id as owner_ref_id, 
            created_time as timestamp, 
            0 as session_index, 
            'Created' as name, 
            json_object(
                'timestamp', created_time,
                'key', the_key,
                'name', name,
                'collection_period', collection_period,
                'metric_unit', metric_unit) as data 
        from metric 
        where ref_id not in (
            select distinct(ref_id)
            from metric m
            join metric_event me 
            on m.ref_id = me.owner_ref_id 
            and me.name = 'Created')
        """)


def downgrade():
    pass
