"""Default value for eisen collection values

Revision ID: ad795c7f1fd8
Revises: 23912567470d
Create Date: 2021-03-30 17:01:17.757610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad795c7f1fd8'
down_revision = '23912567470d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("update metric set collection_eisen=json_array()")


def downgrade():
    pass
