from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy_utils import UUIDType
from marshmallow import Schema, fields
from transient.lib.database import Base
import uuid


MAX_PAYMENT_AMOUNT = Decimal("99999999.99999999")
MIN_PAYMENT_AMOUNT = Decimal("0.00000001")

VALID_CURRENCIES = ("BTC", "LTC", "DOGE")
VALID_STATUSES = ("UNPAID", "PAID", "CONFIRMED", "UNDERPAID", "REFUNDED", "CANCELLED", "EXPIRED")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    currency = Column(Enum(*VALID_CURRENCIES, name="currency_types"), nullable=False)
    amount = Column(Numeric(scale=8, precision=16), nullable=False)
    amount_received = Column(Numeric(scale=8, precision=16), default=0, nullable=False)
    payment_address = Column(String(length=128), nullable=False)
    payee_address = Column(String(length=128), nullable=False)
    confirmations_required = Column(Integer, default=2, nullable=False)
    status = Column(Enum(*VALID_STATUSES, name="status_types"), default="UNPAID", nullable=False)
    transactions = relationship("Transaction", backref="payments")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)

    def to_dict(self):
        from transient.models.transaction import transactions_schema
        transactions = self.transactions
        payment_result = payment_schema.dump(self)
        transactions_result = transactions_schema.dump(transactions)
        payment_data = payment_result.data
        payment_data["transactions"] = transactions_result.data
        return payment_data

    @validates("amount")
    def validate_amount(self, key, amount):
        if amount < MIN_PAYMENT_AMOUNT:
            raise ValueError("Payment amount must be greater than 0")
        elif amount > MAX_PAYMENT_AMOUNT:
            raise ValueError("Payment amount is above the maximum amount")
        else:
            return amount

    @classmethod
    def by_address(cls, address):
        return Payment.query.filter(Payment.payment_address == address).first()


class PaymentSchema(Schema):
    id = fields.Str(dump_only=True)
    currency = fields.Str()
    amount = fields.Decimal()
    amount_received = fields.Decimal(dump_only=True)
    payment_address = fields.Str()
    payee_address = fields.Str(load_only=True)
    confirmations_required = fields.Str(load_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime()


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
