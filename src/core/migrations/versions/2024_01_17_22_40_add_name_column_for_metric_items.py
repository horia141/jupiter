"""Add name column for metric items

Revision ID: 75a742597704
Revises: cb846caea933
Create Date: 2024-01-17 22:40:06.519708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "75a742597704"
down_revision = "cb846caea933"
branch_labels = None
depends_on = None


def upgrade() -> None:

    with op.batch_alter_table("metric_entry") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))

    op.execute(
        """
        UPDATE metric_entry
        SET name = 'Entry for ' || collection_time || ' value=' || value"""
    )


def downgrade():
    pass
