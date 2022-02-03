"""Migrate smart lists to collection


Revision ID: ab86d99564d9
Revises: 6c71cc3b1c7d
Create Date: 2022-02-02 22:42:35.360188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab86d99564d9'
down_revision = '6c71cc3b1c7d'
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
    with op.batch_alter_table('smart_list', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('smart_list_collection_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_smart_list_smart_list_collection_ref_id_smart_list_collection', 'smart_list_collection', ["smart_list_collection_ref_id"], ["ref_id"])
        batch_op.drop_column('workspace_ref_id')


def downgrade() -> None:
    with op.batch_alter_table('smart_list_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('smart_list_collection_ref_id')
