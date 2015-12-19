import uuid
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy_utils import UUIDType
from marshmallow import Schema, fields, pre_load, post_dump
from transient.lib.database import Base
from transient.lib.utils import decimal_to_string


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUIDType(binary=False), primary_key=True)
    payment_id = Column(UUIDType(binary=False), ForeignKey("payments.id"))
    transaction_id = Column(String(length=128), nullable=False, unique=True)
    currency = Column(Enum("BTC", "LTC", "DOGE", name="currency_types"), nullable=False)
    amount = Column(Numeric(scale=8, precision=16), nullable=False)
    fee = Column(Numeric(scale=8, precision=16), nullable=False)
    confirmations = Column(Integer, nullable=False)
    category = Column(String(length=128), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __init__(self, *args, **kwargs):
        self.id = uuid.uuid4()
        self.confirmations = kwargs.get("confirmations", 0)
        super(Transaction, self).__init__(*args, **kwargs)

    def to_dict(self, only=None):
        if only:
            transaction_result = TransactionSchema(only=only).dump(self)
        else:
            transaction_result = TransactionSchema().dump(self)
        return transaction_result.data


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

    @pre_load
    def load_payment_id(self, in_data):
        if "transaction" in in_data:
            in_data["transaction_id"] = in_data["transaction"]
            del in_data["transaction"]
        if "payment" in in_data:
            in_data["payment_id"] = in_data["payment"]
            del in_data["payment"]
        if "payment_id" in in_data:
            in_data['payment_id'] = str(in_data['payment_id'])
        return in_data

    @post_dump
    def dump_decimals_to_string(self, data):
        if "amount" in data:
            data["amount"] = decimal_to_string(data["amount"])
        if "fee" in data:
            data["fee"] = decimal_to_string(data["fee"])
