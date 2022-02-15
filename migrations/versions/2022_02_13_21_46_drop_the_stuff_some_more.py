"""Drop the stuff some more

Revision ID: bf92e32a7363
Revises: 82a9343cb654
Create Date: 2022-02-13 21:46:53.055660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf92e32a7363'
down_revision = '82a9343cb654'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('inbox_task') as batch_op:
        batch_op.drop_column('recurring_type')


def downgrade() -> None:
    pass
