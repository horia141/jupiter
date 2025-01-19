"""Drop accepted_time columns

Revision ID: 1930a77198c2
Revises: 5d8f4dea8ebb
Create Date: 2025-01-19 21:37:43.866033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1930a77198c2'
down_revision = '5d8f4dea8ebb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("inbox_task") as batch_op:
            batch_op.drop_column("accepted_time")
    except KeyError:
        pass
    try:
        with op.batch_alter_table("big_plan") as batch_op:
            batch_op.drop_column("accepted_time")
    except KeyError:
        pass


def downgrade() -> None:
    pass
