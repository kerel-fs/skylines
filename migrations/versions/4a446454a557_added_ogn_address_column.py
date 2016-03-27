# revision identifiers, used by Alembic.
revision = '4a446454a557'
down_revision = '36d3b413b8d9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('ogn_address', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('users', 'ogn_address')