"""Add lucky puppy column

Revision ID: 332900a57518
Revises: 44758da7bd17
Create Date: 2023-10-14 17:25:11.893214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '332900a57518'
down_revision = '44758da7bd17'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("gamification_score_log_entry") as batch_op:
        batch_op.add_column(sa.Column("has_lucky_puppy_bonus", sa.Boolean, nullable=True))

def downgrade():
    pass
