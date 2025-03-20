"""Drop key columns

Revision ID: c7662aa06439
Revises: 1706db08b534
Create Date: 2023-06-19 15:51:03.232928

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "c7662aa06439"
down_revision = "1706db08b534"
branch_labels = None
depends_on = None


def upgrade():
    try:
        with op.batch_alter_table("project") as batch_op:
            batch_op.drop_column("the_key")
    except KeyError:
        pass
    try:
        with op.batch_alter_table("metric") as batch_op:
            batch_op.drop_column("the_key")
    except KeyError:
        pass
    try:
        with op.batch_alter_table("smart_list") as batch_op:
            batch_op.drop_column("the_key")
    except KeyError:
        pass


def downgrade():
    pass
