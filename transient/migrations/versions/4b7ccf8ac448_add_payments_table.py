"""Add payments table

Revision ID: 4b7ccf8ac448
Create Date: 2015-12-14 20:13:00.029117

"""

# revision identifiers, used by Alembic.
revision = '4b7ccf8ac448'
down_revision = None
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('currency', postgresql.ENUM(u'BTC', u'LTC', u'DOGE', name='currency_types'), autoincrement=False, nullable=False),
        sa.Column('amount', sa.NUMERIC(precision=16, scale=8), autoincrement=False, nullable=False),
        sa.Column('payment_address', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
        sa.Column('merchant_address', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
        sa.Column('confirmations_required', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('status', postgresql.ENUM(u'UNPAID', u'PAID', u'CONFIRMED', u'UNDERPAID', u'REFUNDED', u'CANCELLED', u'EXPIRED', name='status_types'), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name=u'payments_pkey'),
        postgresql_ignore_search_path=False
    )


def downgrade():
    op.drop_table('payments')
