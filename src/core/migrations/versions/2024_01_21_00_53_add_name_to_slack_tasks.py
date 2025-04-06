"""Add name to slack tasks

Revision ID: b7bcd663ae4e
Revises: 493273686d33
Create Date: 2024-01-21 00:53:13.460559

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7bcd663ae4e"
down_revision = "493273686d33"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("slack_task") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade() -> None:
    pass
