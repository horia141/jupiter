"""Add new kind field to events tables and backfill the value

Revision ID: 5fe8147f542c
Revises: 670ea976fe9f
Create Date: 2021-12-26 22:50:11.688817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fe8147f542c'
down_revision = '670ea976fe9f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        alter table person_event
        add column kind VARCHAR(16);""")
    op.execute("""
        update person_event
        set kind = 'create'
        where name = 'Created' and kind is Null;""")
    op.execute("""
        update person_event
        set kind = 'archived'
        where name = 'Archived' and kind is Null;""")
    op.execute("""
        update person_event
        set kind = 'update'
        where kind is Null;""")
    op.execute("""
        alter table prm_database_event
        add column kind VARCHAR(16);""")
    op.execute("""
        update prm_database_event
        set kind = 'create'
        where name = 'Created' and kind is Null;""")
    op.execute("""
        update prm_database_event
        set kind = 'archived'
        where name = 'Archived' and kind is Null;""")
    op.execute("""
        update prm_database_event
        set kind = 'update'
        where kind is Null;""")
    op.execute("""
        alter table metric_entry_event
        add column kind VARCHAR(16);""")
    op.execute("""
        update metric_entry_event
        set kind = 'create'
        where name = 'Created' and kind is Null;""")
    op.execute("""
        update metric_entry_event
        set kind = 'archived'
        where name = 'Archived' and kind is Null;""")
    op.execute("""
        update metric_entry_event
        set kind = 'update'
        where kind is Null;""")
    op.execute("""
        alter table metric_event
        add column kind VARCHAR(16);""")
    op.execute("""
        update metric_event
        set kind = 'create'
        where name = 'Created' and kind is Null;""")
    op.execute("""
        update metric_event
        set kind = 'archived'
        where name = 'Archived' and kind is Null;""")
    op.execute("""
        update metric_event
        set kind = 'update'
        where kind is Null;""")


def downgrade():
    pass
