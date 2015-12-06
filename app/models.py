from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import validates, relationship, backref
from sqlalchemy_utils import UUIDType
from marshmallow import Schema, fields, ValidationError, pre_load
from app.database import Base
import uuid


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    currency = Column(Enum("BTC", "LTC", "DOGE", name="currency_types"), nullable=False)
    amount = Column(Numeric(scale=8, precision=16), nullable=False)
    amount_recieved = Column(Numeric(scale=8, precision=16), default=0, nullable=False)
    payment_address = Column(String(length=128), nullable=False)
    payee_address = Column(String(length=128), nullable=False)
    confirmations_required = Column(Integer, default=2, nullable=False)
    status = Column(Enum("UNPAID", "PAID", "CONFIRMED", "UNDERPAID", "REFUNDED",
        "CANCELLED", "EXPIRED", name="status_types"), default="UNPAID", nullable=False)
    transactions = relationship("Transaction", backref="payments")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)


class PaymentSchema(Schema):
    id = fields.Str(dump_only=True)
    currency = fields.Str()
    amount = fields.Decimal()
    amount_recieved = fields.Decimal(dump_only=True)
    payment_address = fields.Str()
    payee_address = fields.Str(load_only=True)
    confirmations_required = fields.Str(load_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime()


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    payment_id = Column(UUIDType(binary=False), ForeignKey("payments.id"))
    transaction_id = Column(String(length=128), nullable=False, unique=True)
    currency = Column(Enum("BTC", "LTC", "DOGE", name="currency_types"), nullable=False)
    amount = Column(Numeric(scale=8, precision=16), nullable=False)
    fee = Column(Numeric(scale=8, precision=16), nullable=False)
    confirmations = Column(Integer, default=0, nullable=False)
    category = Column(String(length=128), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime)


class TransactionSchema(Schema):
    id = fields.Str(dump_only=True)
    payment_id = fields.Str()
    transaction_id = fields.Str()
    currency = fields.Str()
    amount = fields.Decimal()
    fee = fields.Decimal()
    confirmations = fields.Integer()
    category = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    sent_at = fields.DateTime()


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
