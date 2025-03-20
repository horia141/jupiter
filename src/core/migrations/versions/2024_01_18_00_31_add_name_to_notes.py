"""Add name to notes

Revision ID: 37dd9d715387
Revises: 4933a4869c5b
Create Date: 2024-01-18 00:31:13.114419

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "37dd9d715387"
down_revision = "4933a4869c5b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("note") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade():
    pass
