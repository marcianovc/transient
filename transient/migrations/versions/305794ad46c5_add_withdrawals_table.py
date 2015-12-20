"""Add withdrawals table

Revision ID: 305794ad46c5
Revises: 392c0a07a3c
Create Date: 2015-12-19 21:22:36.390203

"""

# revision identifiers, used by Alembic.

revision = '305794ad46c5'
down_revision = '392c0a07a3c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('withdrawals',
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('payment_id', postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
        sa.Column('currency', postgresql.ENUM(u'BTC', u'LTC', u'DOGE', name='currency_types', create_type=False), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['payment_id'], [u'payments.id'], name=u'withdrawals_payment_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'withdrawals_pkey'),
        sa.UniqueConstraint('transaction_id', name=u'withdrawals_transaction_id_key')
    )


def downgrade():
    op.drop_table('withdrawals')
