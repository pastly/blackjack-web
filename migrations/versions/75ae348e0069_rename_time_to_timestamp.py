"""rename time to timestamp

Revision ID: 75ae348e0069
Revises: ec9146a96270
Create Date: 2020-04-30 16:22:52.119658

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '75ae348e0069'
down_revision = 'ec9146a96270'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('basic_strategy_play_stats', 'time', new_column_name='timestamp')


def downgrade():
    op.alter_column('basic_strategy_play_stats', 'timestamp', new_column_name='time')
