"""Add eisen and difficulty for big plans

Revision ID: 4487471c6629
Revises: 7179356b640d
Create Date: 2025-04-24 00:07:47.123595

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4487471c6629"
down_revision = "7179356b640d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("big_plan") as batch_op:
        batch_op.add_column(sa.Column("eisen", sa.String()))
        batch_op.add_column(sa.Column("difficulty", sa.String()))

    op.execute("UPDATE big_plan SET eisen = 'regular' WHERE eisen is null")
    op.execute("UPDATE big_plan SET difficulty = 'easy' WHERE difficulty is null")


def downgrade() -> None:
    with op.batch_alter_table("big_plan") as batch_op:
        batch_op.drop_column("eisen")
        batch_op.drop_column("difficulty")
