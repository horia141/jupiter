"""Alter nullable slack table

Revision ID: 346d70771b6f
Revises: 04fc03a337b3
Create Date: 2022-03-25 18:58:51.668686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '346d70771b6f'
down_revision = '04fc03a337b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {
        "fk":
            "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("slack_task", naming_convention=naming_convention) as batch_op:
        batch_op.alter_column('channel', existing_type=sa.String, nullable=True)
        batch_op.alter_column('message', existing_type=sa.String, nullable=False)
        batch_op.alter_column('generation_extra_info', existing_type=sa.String, nullable=False)


def downgrade() -> None:
    pass