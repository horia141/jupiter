"""Add source field and backfill

Revision ID: 84647802c926
Revises: 783ed9de38cf
Create Date: 2022-01-07 19:24:07.330944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84647802c926'
down_revision = '783ed9de38cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        alter table metric_event add column source VARCHAR;
    """)
    op.execute("""
        update metric_event
        set source='cli'
        where source is null
    """)
    op.execute("""
        alter table metric_entry_event add column source VARCHAR;
    """)
    op.execute("""
        update metric_entry_event
        set source='notion'
        where source is null
    """)
    op.execute("""
        alter table prm_database_event add column source VARCHAR;
    """)
    op.execute("""
        update prm_database_event
        set source='cli'
        where source is null
    """)
    op.execute("""
        alter table person_event add column source VARCHAR;
    """)
    op.execute("""
        update person_event
        set source='notion'
        where source is null
    """)


def downgrade() -> None:
    pass
