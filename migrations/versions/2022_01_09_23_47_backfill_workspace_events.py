"""Backfill workspace events

Revision ID: 31695e3a6ce7
Revises: b69752a0bf11
Create Date: 2022-01-09 23:47:10.011093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31695e3a6ce7'
down_revision = 'b69752a0bf11'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        insert into workspace_event
            (owner_ref_id, timestamp, session_index, name, source, owner_version, kind, data) 
        select 
            ref_id as owner_ref_id, 
            created_time as timestamp,
            0 as session_index,
            'Created' as name,
            'cli' as source,
            1 as owner_version,
            'created' as kind,
            '{}' as data
        from workspace;
    """)
    op.execute("""
        insert into workspace_event
            (owner_ref_id, timestamp, session_index, name, source, owner_version, kind, data) 
        select 
            ref_id as owner_ref_id, 
            last_modified_time as timestamp,
            0 as session_index,
            'Updated' as name,
            'cli' as source,
            2 as owner_version,
            'updated' as kind,
            '{}' as data
        from workspace
        where last_modified_time > created_time;
    """)
    op.execute("""
        update workspace
        set version=version+1
        where last_modified_time > created_time;
    """)


def downgrade() -> None:
    pass
