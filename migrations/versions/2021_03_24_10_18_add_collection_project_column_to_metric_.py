"""Add collection project column to metric table

Revision ID: 834b07e1bb4f
Revises: ce847ba7aebe
Create Date: 2021-03-24 10:18:50.719197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '834b07e1bb4f'
down_revision = 'ce847ba7aebe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('metric', sa.Column('collection_project_ref_id', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('metric', 'collection_project_ref_id')
