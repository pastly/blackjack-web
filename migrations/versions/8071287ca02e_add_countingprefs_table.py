"""Add CountingPrefs table

Revision ID: 8071287ca02e
Revises: aa4feccd69de
Create Date: 2020-08-09 13:09:24.415101

"""
from alembic import op
import sqlalchemy as sa
import app


# revision identifiers, used by Alembic.
revision = '8071287ca02e'
down_revision = 'aa4feccd69de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('counting_prefs',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('prefs', app.models.GzippedBytes(length=1024), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('counting_prefs')
    # ### end Alembic commands ###
