import unittest
from decimal import Decimal
import uuid
from mixer.backend.sqlalchemy import Mixer
from transient.lib.database import session, init_db
from transient.models.payment import Payment
from transient.models.transaction import Transaction
import random


valid_addresses = [
    "DGMJjZjgdGDmgk21PARUajeUpGNrpq6kph",
    "DQJJoovaB2zhiJuTELsAmMpEZJEwDHEULa",
    "DESYhBxmHJXd2rgszzDpK2K7uGVreLTviL",
    "D5Km7yuVkJnPGWHf2UfvNMxLDwGsMDn9ya",
    "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx"
]

def get_uuid():
    return uuid.uuid4()

def get_address():
    return random.choice(valid_addresses)

def get_amount():
    return Decimal(random.randint(1,100))


class BaseTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(BaseTestCase, self).__init__(methodName)
        self.mixer = Mixer(session=session, commit=False)
        self.session = session
        init_db()
        self.mixer.register(Payment, id=get_uuid, payment_address=get_address, merchant_address=get_address,
                            amount=get_amount)
        self.mixer.register(Transaction, id=get_uuid, amount=get_amount, fee=Decimal(1))
