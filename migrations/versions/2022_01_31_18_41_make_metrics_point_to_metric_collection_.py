"""Make metrics point to metric collection table

Revision ID: 60da918ce56e
Revises: 73a00d90c1ff
Create Date: 2022-01-31 18:41:49.645255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60da918ce56e'
down_revision = '73a00d90c1ff'
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
    with op.batch_alter_table('metric', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('metric_collection_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_metric_metric_collection_ref_id_metric_collection', 'metric_collection', ["metric_collection_ref_id"], ["ref_id"])
        batch_op.drop_column('workspace_ref_id')


def downgrade() -> None:
    with op.batch_alter_table('metric_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('metric_collection_ref_id')
