"""Add transactions table

Revision ID: 392c0a07a3c
Revises: 4b7ccf8ac448
Create Date: 2015-12-14 20:13:06.833508

"""

# revision identifiers, used by Alembic.
revision = '392c0a07a3c'
down_revision = '4b7ccf8ac448'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('transactions',
        sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column('payment_id', postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
        sa.Column('currency', postgresql.ENUM(u'BTC', u'LTC', u'DOGE', name='currency_types'), autoincrement=False, nullable=False),
        sa.Column('amount', sa.NUMERIC(precision=16, scale=8), autoincrement=False, nullable=False),
        sa.Column('fee', sa.NUMERIC(precision=16, scale=8), autoincrement=False, nullable=False),
        sa.Column('confirmations', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('category', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['payment_id'], [u'payments.id'], name=u'transactions_payment_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'transactions_pkey'),
        sa.UniqueConstraint('transaction_id', name=u'transactions_transaction_id_key')
    )


def downgrade():
    op.drop_table('transactions')
