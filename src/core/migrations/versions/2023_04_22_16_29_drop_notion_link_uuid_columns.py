"""Drop notion link uuid columns

Revision ID: bb9cf0028fc1
Revises: 7e8c0bc468ca
Create Date: 2023-04-22 16:29:21.969529

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bb9cf0028fc1"
down_revision = "7e8c0bc468ca"
branch_labels = None
depends_on = None


def upgrade():
    try:
        with op.batch_alter_table("project") as batch_op:
            batch_op.drop_column("notion_link_uuid")
    except KeyError:
        pass
    try:
        with op.batch_alter_table("big_plan") as batch_op:
            batch_op.drop_column("notion_link_uuid")
    except KeyError:
        pass


def downgrade():
    pass
