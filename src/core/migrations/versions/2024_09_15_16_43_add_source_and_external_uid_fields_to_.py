"""Add source and external_uid fields to schedule events

Revision ID: b91f4501b574
Revises: 6c4757c48546
Create Date: 2024-09-15 16:43:26.332245

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b91f4501b574"
down_revision = "6c4757c48546"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("schedule_event_full_days") as batch_op:
        batch_op.add_column(sa.Column("source", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("external_uid", sa.String(), nullable=True))

    with op.batch_alter_table("schedule_event_in_day") as batch_op:
        batch_op.add_column(sa.Column("source", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("external_uid", sa.String(), nullable=True))

    op.execute(
        """ 
        update schedule_event_full_days
        set source = 'user'
        where source is null;
    """
    )
    op.execute(
        """ 
        update schedule_event_in_day
        set source = 'user'
        where source is null;
    """
    )


def downgrade() -> None:
    pass
