"""Drop the start and end columns of habits

Revision ID: 155b641a787c
Revises: bf92e32a7363
Create Date: 2022-02-13 22:52:11.730173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '155b641a787c'
down_revision = 'bf92e32a7363'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('habit') as batch_op:
        batch_op.drop_column('start_at_date')
        batch_op.drop_column('end_at_date')


def downgrade() -> None:
    pass
