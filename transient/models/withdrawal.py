import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy_utils import UUIDType
from marshmallow import Schema, fields, pre_load
from transient.lib.database import Base


class Withdrawal(Base):
    __tablename__ = "withdrawals"
    id = Column(UUIDType(binary=False), primary_key=True)
    payment_id = Column(UUIDType(binary=False), ForeignKey("payments.id"))
    transaction_id = Column(String(length=128), nullable=False, unique=True)
    currency = Column(Enum("BTC", "LTC", "DOGE", name="currency_types"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __init__(self, *args, **kwargs):
        self.id = uuid.uuid4()
        super(Withdrawal, self).__init__(*args, **kwargs)

    def to_dict(self, only=None):
        if only:
            withdrawal_result = WithdrawalSchema(only=only).dump(self)
        else:
            withdrawal_result = WithdrawalSchema().dump(self)
        return withdrawal_result.data

    @classmethod
    def from_dict(cls, raw_data):
        data, errors = WithdrawalSchema().load(raw_data)
        return cls(**data)

    @staticmethod
    def by_payment(payment_id):
        return Withdrawal.query.filter(Withdrawal.payment_id == str(payment_id)).first()


class WithdrawalSchema(Schema):
    id = fields.Str(dump_only=True)
    payment_id = fields.Str()
    transaction_id = fields.Str()
    currency = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def load_payment_id(self, in_data):
        if "payment_id" in in_data:
            in_data['payment_id'] = str(in_data['payment_id'])
        return in_data
