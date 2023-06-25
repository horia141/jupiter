"""Drop timezone from workspace

Revision ID: 1706db08b534
Revises: 8ff8e9bc097d
Create Date: 2023-06-19 14:17:23.146236

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1706db08b534"
down_revision = "8ff8e9bc097d"
branch_labels = None
depends_on = None


def upgrade():
    try:
        with op.batch_alter_table("workspace") as batch_op:
            batch_op.drop_column("timezone")
    except KeyError:
        pass


def downgrade():
    pass
