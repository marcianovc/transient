import uuid
import numbers
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy_utils import UUIDType
from marshmallow import Schema, fields, pre_load
from transient.lib.database import Base
from transient.models.transaction import TransactionSchema



MAX_PAYMENT_AMOUNT = Decimal("99999999.99999999")
MIN_PAYMENT_AMOUNT = Decimal("0.00000001")

VALID_CURRENCIES = ("BTC", "LTC", "DOGE")
VALID_STATUSES = ("UNPAID", "PAID", "CONFIRMED", "UNDERPAID", "REFUNDED", "CANCELLED", "EXPIRED")


def validate_amount(amount):
    if not isinstance(amount, numbers.Number):
        raise ValueError("Payment amount must be a number")
    elif amount < MIN_PAYMENT_AMOUNT:
        raise ValueError("Payment amount must be greater than 0")
    elif amount > MAX_PAYMENT_AMOUNT:
        raise ValueError("Payment amount is above the maximum amount")
    else:
        return amount


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUIDType(binary=False), primary_key=True)
    currency = Column(Enum(*VALID_CURRENCIES, name="currency_types"), nullable=False)
    amount = Column(Numeric(scale=8, precision=16), nullable=False)
    payment_address = Column(String(length=128), nullable=False)
    merchant_address = Column(String(length=128), nullable=False)
    confirmations_required = Column(Integer, nullable=False)
    status = Column(Enum(*VALID_STATUSES, name="status_types"), nullable=False)
    transactions = relationship("Transaction", backref="payments")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)

    def __init__(self, *args, **kwargs):
        self.id = uuid.uuid4()
        self.confirmations_required = kwargs.get("confirmations_required", 2)
        self.status = kwargs.get("status", "UNPAID")
        super(Payment, self).__init__(*args, **kwargs)

    def amount_received(self):
        amounts_received = map(lambda t: t.amount, self.transactions)
        if not amounts_received:
            return Decimal("0")
        else:
            return reduce(lambda x, y: x + y, amounts_received)

    def amount_confirmed(self):
        confirmed_transactions = filter(lambda t: t.confirmations >= self.confirmations_required, self.transactions)
        amounts_confirmed = map(lambda t: t.amount, confirmed_transactions)
        if not amounts_confirmed:
            return Decimal("0")
        else:
            return reduce(lambda x, y: x + y, amounts_confirmed)

    def to_dict(self, only=None):
        if only:
            payment_result = PaymentSchema(only=only).dump(self)
        else:
            payment_result = PaymentSchema().dump(self)
        return payment_result.data

    @validates("amount")
    def validate_amount(self, key, amount):
        return validate_amount(amount)

    @classmethod
    def by_address(cls, address):
        return Payment.query.filter(Payment.payment_address == address).first()


class PaymentSchema(Schema):
    id = fields.Str(dump_only=True)
    currency = fields.Str()
    amount = fields.Decimal(validate=[validate_amount])
    amount_received = fields.Method("get_amount_received")
    amount_confirmed = fields.Method("get_amount_confirmed")
    payment_address = fields.Str()
    merchant_address = fields.Str(load_only=True)
    confirmations_required = fields.Str(load_only=True)
    status = fields.Str(dump_only=True)
    transactions = fields.Nested(TransactionSchema, many=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime()

    @pre_load
    def load_address_alias(self, data):
        if not isinstance(data.get("amount"), numbers.Number):
            data["amount"] = 0
        if data.get("address"):
            data["merchant_address"] = data.get("address")
        return data

    def get_amount_received(self, obj):
        return obj.amount_received()

    def get_amount_confirmed(self, obj):
        return obj.amount_confirmed()
