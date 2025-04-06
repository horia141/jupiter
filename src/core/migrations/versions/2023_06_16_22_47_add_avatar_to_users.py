"""Add avatar to users

Revision ID: 8ff8e9bc097d
Revises: 039c2afe8bcb
Create Date: 2023-06-16 22:47:36.296517

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8ff8e9bc097d"
down_revision = "039c2afe8bcb"
branch_labels = None
depends_on = None


def upgrade():
    naming_convention = {
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("user", naming_convention=naming_convention) as batch_op:
        batch_op.add_column(sa.Column("avatar", sa.String))

    op.execute(
        """
        update user set avatar='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHBvaW50ZXItZXZlbnRzPSJub25lIiB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCI+IDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiByeD0iMCIgcnk9IjAiIHN0eWxlPSJmaWxsOiAjYzAzOTJiIj48L3JlY3Q+IDx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHk9IjUwJSIgeD0iNTAlIiBkeT0iMC4zNWVtIiBwb2ludGVyLWV2ZW50cz0iYXV0byIgZmlsbD0iI2ZmZmZmZiIgZm9udC1mYW1pbHk9IkhlbHZldGljYU5ldWUtTGlnaHQsSGVsdmV0aWNhIE5ldWUgTGlnaHQsSGVsdmV0aWNhIE5ldWUsSGVsdmV0aWNhLEFyaWFsLEx1Y2lkYSBHcmFuZGUsc2Fucy1zZXJpZiIgc3R5bGU9ImZvbnQtd2VpZ2h0OiA0MDA7IGZvbnQtc2l6ZTogODBweCI+SEM8L3RleHQ+IDwvc3ZnPg=='
    """
    )

    with op.batch_alter_table("user", naming_convention=naming_convention) as batch_op:
        batch_op.alter_column("avatar", nullable=True)


def downgrade():
    try:
        with op.batch_alter_table("user") as batch_op:
            batch_op.drop_column("avatar")
    except KeyError:
        pass
