"""Drop timezone column in time events

Revision ID: 5fd8a6a670e4
Revises: 5bd25a8a7c69
Create Date: 2024-09-21 11:42:30.474924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fd8a6a670e4'
down_revision = '5bd25a8a7c69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("time_event_in_day_block") as batch_op:
            batch_op.drop_column("timezone")
    except KeyError:
        pass


def downgrade() -> None:
    pass
