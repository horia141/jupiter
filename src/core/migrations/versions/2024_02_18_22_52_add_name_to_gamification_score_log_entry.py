"""Add name to gamification_score_log_entry

Revision ID: cc1a2f1e3d35
Revises: dad9d96b473b
Create Date: 2024-02-18 22:52:45.039738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cc1a2f1e3d35"
down_revision = "dad9d96b473b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("gamification_score_log_entry") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String, nullable=True))


def downgrade():
    pass
