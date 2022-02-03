"""Rename prm database

Revision ID: f2b82bd81fca
Revises: ab86d99564d9
Create Date: 2022-02-03 12:09:22.866448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2b82bd81fca'
down_revision = 'ab86d99564d9'
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
    op.create_table(
        'person_collection',
        sa.Column('ref_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('archived', sa.Boolean, nullable=False),
        sa.Column('created_time', sa.DateTime, nullable=False),
        sa.Column('last_modified_time', sa.DateTime, nullable=False),
        sa.Column('archived_time', sa.DateTime, nullable=True),
        sa.Column('workspace_ref_id', sa.Integer, sa.ForeignKey('workspace.ref_id'), unique=True, index=True, nullable=False),
        sa.Column('catch_up_project_ref_id', sa.Integer, sa.ForeignKey('project.ref_id'), nullable=False))
    op.create_table(
        'person_collection_event',
        sa.Column('owner_ref_id', sa.Integer, sa.ForeignKey('person_collection.ref_id'), primary_key=True),
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('session_index', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32), primary_key=True),
        sa.Column('source', sa.String(16), nullable=False),
        sa.Column('owner_version', sa.Integer, nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('data', sa.JSON, nullable=True))
    with op.batch_alter_table('person', naming_convention=convention) as batch_op:
        batch_op.add_column(sa.Column('person_collection_ref_id', sa.Integer, index=True, nullable=True))
        batch_op.create_foreign_key('fk_person_person_collection_ref_id_person_collection', 'person_collection', ["person_collection_ref_id"], ["ref_id"])
        batch_op.drop_column('prm_database_ref_id')


def downgrade() -> None:
    with op.batch_alter_table('person_collection', naming_convention=convention) as batch_op:
        batch_op.drop_column('prm_database_ref_id')
    op.drop_table('person_collection_event')
    op.drop_table('person_collection')
