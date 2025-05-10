"""Add fields for home config

Revision ID: 236220c9ed53
Revises: 625fd14020f4
Create Date: 2025-05-09 21:10:02.610540

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "236220c9ed53"
down_revision = "625fd14020f4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("home_config") as batch_op:
        batch_op.add_column(sa.Column("desktop_config", sa.JSON()))
        batch_op.add_column(sa.Column("mobile_config", sa.JSON()))

    op.execute(
        """
        UPDATE home_config
        SET desktop_config = '{"tabs": []}', mobile_config = '{"tabs": []}'
        WHERE desktop_config IS NULL OR mobile_config IS NULL
        """
    )


def downgrade():
    with op.batch_alter_table("home_config") as batch_op:
        batch_op.drop_column("desktop_config")
        batch_op.drop_column("mobile_config")
