"""Add is_key field to entities

Revision ID: 625fd14020f4
Revises: 20190c88fbc1
Create Date: 2025-05-04 19:23:02.960961

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "625fd14020f4"
down_revision = "20190c88fbc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("habit") as batch_op:
        batch_op.add_column(sa.Column("is_key", sa.Boolean(), nullable=True))

    op.execute("UPDATE habit SET is_key = FALSE where is_key is NULL")

    with op.batch_alter_table("habit") as batch_op:
        batch_op.alter_column("is_key", nullable=False)

    with op.batch_alter_table("chore") as batch_op:
        batch_op.add_column(sa.Column("is_key", sa.Boolean(), nullable=True))

    op.execute("UPDATE chore SET is_key = FALSE where is_key is NULL")

    with op.batch_alter_table("chore") as batch_op:
        batch_op.alter_column("is_key", nullable=False)

    with op.batch_alter_table("big_plan") as batch_op:
        batch_op.add_column(sa.Column("is_key", sa.Boolean(), nullable=True))

    op.execute("UPDATE big_plan SET is_key = FALSE where is_key is NULL")

    with op.batch_alter_table("big_plan") as batch_op:
        batch_op.alter_column("is_key", nullable=False)

    with op.batch_alter_table("inbox_task") as batch_op:
        batch_op.add_column(sa.Column("is_key", sa.Boolean(), nullable=True))

    op.execute("UPDATE inbox_task SET is_key = FALSE where is_key is NULL")

    with op.batch_alter_table("inbox_task") as batch_op:
        batch_op.alter_column("is_key", nullable=False)

    with op.batch_alter_table("metric") as batch_op:
        batch_op.add_column(sa.Column("is_key", sa.Boolean(), nullable=True))

    op.execute("UPDATE metric SET is_key = FALSE where is_key is NULL")

    with op.batch_alter_table("metric") as batch_op:
        batch_op.alter_column("is_key", nullable=False)

    with op.batch_alter_table("home_config") as batch_op:
        batch_op.drop_column("key_habits")
        batch_op.drop_column("key_metrics")


def downgrade() -> None:
    with op.batch_alter_table("habit") as batch_op:
        batch_op.drop_column("is_key")

    with op.batch_alter_table("chore") as batch_op:
        batch_op.drop_column("is_key")

    with op.batch_alter_table("big_plan") as batch_op:
        batch_op.drop_column("is_key")

    with op.batch_alter_table("inbox_task") as batch_op:
        batch_op.drop_column("is_key")

    with op.batch_alter_table("metric") as batch_op:
        batch_op.drop_column("is_key")
