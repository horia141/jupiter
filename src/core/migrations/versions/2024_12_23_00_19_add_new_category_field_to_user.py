"""Add new category field to user

Revision ID: f858598fb7b3
Revises: 9232b5ece952
Create Date: 2024-12-23 00:19:13.234339

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f858598fb7b3"
down_revision = "9232b5ece952"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new column category to user table
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("user", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column("category", sa.String))

    op.execute(
        """
        update user set category='standard'
        """
    )

    with op.batch_alter_table("user", naming_convention=naming_convention) as batch_op:
        batch_op.alter_column("category", nullable=True)


def downgrade() -> None:
    try:
        with op.batch_alter_table("user") as batch_op:
            batch_op.drop_column("category")
    except KeyError:
        pass
