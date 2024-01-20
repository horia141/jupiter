"""Add name to email tasks

Revision ID: d074ebd1c713
Revises: b7bcd663ae4e
Create Date: 2024-01-21 00:55:54.418897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d074ebd1c713"
down_revision = "b7bcd663ae4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("email_task") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade() -> None:
    pass
