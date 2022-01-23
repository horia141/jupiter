"""Create Person tables

Revision ID: 0c393dd2ea3c
Revises: 8496fe20331d
Create Date: 2021-05-05 17:18:30.174469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c393dd2ea3c'
down_revision = '8496fe20331d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'person',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('relationship', sa.String(), nullable=False),
        sa.Column('catch_up_project_ref_id', sa.Integer, nullable=True),
        sa.Column('catch_up_period', sa.String(), nullable=True),
        sa.Column('catch_up_eisen', sa.JSON, nullable=True),
        sa.Column('catch_up_difficulty', sa.String, nullable=True),
        sa.Column('catch_up_actionable_from_day', sa.Integer, nullable=True),
        sa.Column('catch_up_actionable_from_month', sa.Integer, nullable=True),
        sa.Column('catch_up_due_at_time', sa.String, nullable=True),
        sa.Column('catch_up_due_at_day', sa.Integer, nullable=True),
        sa.Column('catch_up_due_at_month', sa.Integer, nullable=True),
        sa.Column('birthday', sa.String(), nullable=True))
    op.create_table(
        'person_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('person.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('person')
    op.drop_table('person_event')
