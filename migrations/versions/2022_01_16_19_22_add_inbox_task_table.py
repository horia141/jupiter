"""Add inbox task table

Revision ID: 9b37770abd4d
Revises: bd7279dd5af1
Create Date: 2022-01-16 19:22:06.791381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b37770abd4d'
down_revision = 'bd7279dd5af1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'inbox_task',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('inbox_task_collection_ref_id', sa.Integer, sa.ForeignKey("inbox_task_collection.ref_id"), index=True, nullable=False),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('big_plan_ref_id', sa.Integer, sa.ForeignKey('big_plan.ref_id'), index=True, nullable=True),
        sa.Column('recurring_task_ref_id', sa.Integer, sa.ForeignKey('recurring_task.ref_id'), index=True, nullable=True),
        sa.Column('metric_ref_id', sa.Integer, sa.ForeignKey('metric.ref_id'), index=True, nullable=True),
        sa.Column('person_ref_id', sa.Integer, sa.ForeignKey('person.ref_id'), index=True, nullable=True),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('eisen', sa.String(20), nullable=False),
        sa.Column('difficulty', sa.String(10), nullable=True),
        sa.Column('actionable_date', sa.DateTime, nullable=True),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('recurring_timeline', sa.String, nullable=True),
        sa.Column('recurring_type', sa.String, nullable=True),
        sa.Column('recurring_gen_right_now', sa.DateTime, nullable=True),
        sa.Column('accepted_time', sa.DateTime, nullable=True),
        sa.Column('working_time', sa.DateTime, nullable=True),
        sa.Column('completed_time', sa.DateTime, nullable=True))
    op.create_table(
        'inbox_task_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('inbox_task.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))


def downgrade() -> None:
    op.drop_table('inbox_task_event')
    op.drop_table('inbox_task')
