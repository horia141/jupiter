"""Add use cases invocation log table

Revision ID: f0413820dee6
Revises: c1db7da45ef5
Create Date: 2022-01-24 19:49:50.843101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0413820dee6'
down_revision = 'c1db7da45ef5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'use_case_mutation_use_case_invocation_record',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('name', sa.String, primary_key=True),
        sa.Column('args', sa.JSON, nullable=False),
        sa.Column('result', sa.String, nullable=False),
        sa.Column('error_str', sa.String, nullable=True))


def downgrade() -> None:
    op.drop_table('use_case_mutation_use_case_invocation_record')
