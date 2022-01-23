"""Create PRM database tables

Revision ID: 8496fe20331d
Revises: ad795c7f1fd8
Create Date: 2021-05-05 17:16:14.369541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8496fe20331d'
down_revision = 'ad795c7f1fd8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'prm_database',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('catch_up_project_ref_id', sa.Integer, nullable=False))
    op.create_table(
        'prm_database_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('prm_database.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('prm_database')
    op.drop_table('prm_database_event')
