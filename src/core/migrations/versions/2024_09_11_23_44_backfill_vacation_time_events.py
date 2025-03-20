"""Backfill vacation time events

Revision ID: 6c4757c48546
Revises: 771083f238d7
Create Date: 2024-09-11 23:44:09.075957

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "6c4757c48546"
down_revision = "771083f238d7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO time_event_full_days_block
        SELECT
            sq.ref_id * 10000 + sq.ref_id as ref_id,
            1 as version,
            sq.archived as archived,
            sq.created_time as created_time,
            sq.created_time as last_modified_time,
            sq.archived_time as archived_time,
            sq.parent_ref_id as time_event_domain_ref_id,
            'NOT-USED' as name,
            'vacation' as namespace,
            sq.ref_id as source_entity_ref_id,
            start_date as start_date,
            cast ((julianday(end_date) - julianday(start_date)) As Integer) as duration_days,
            end_date as end_date
        FROM (
            SELECT
                 td.ref_id as parent_ref_id,
                 va.ref_id as ref_id,
                 va.created_time as created_time,
                 va.last_modified_time as last_modified_time,
                 va.archived_time as archived_time,
                 va.archived as archived,
                 va.start_date as start_date,
                 va.end_date as end_date
            FROM vacation va 
            JOIN vacation_collection vac 
            ON va.vacation_collection_ref_id = vac.ref_id
            JOIN time_event_domain td 
            ON td.workspace_ref_id=vac.workspace_ref_id
        ) as sq;
        """
    )


def downgrade():
    pass
