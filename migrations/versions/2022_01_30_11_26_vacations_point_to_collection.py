"""Vacations point to collection

Revision ID: 6a122bdc1691
Revises: cd61bc9611aa
Create Date: 2022-01-30 11:26:11.101973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a122bdc1691'
down_revision = 'cd61bc9611aa'
branch_labels = None
depends_on = None

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


def upgrade() -> None:
    with op.batch_alter_table('vacation', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('vacation_collection_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_vacation_vacation_collection_ref_id_vacation_collection', 'vacation_collection', ["vacation_collection_ref_id"], ["ref_id"])
        batch_op.drop_column('workspace_ref_id')


def downgrade() -> None:
    with op.batch_alter_table('vacation_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('vacation_collection_ref_id')
