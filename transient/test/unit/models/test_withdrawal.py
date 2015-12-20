import re
from decimal import Decimal
import uuid
import six
from transient.test.unit import BaseTestCase
from transient.models.withdrawal import Withdrawal


class TestWithdrawalModel(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    def test_defaults(self):
        withdrawal = Withdrawal()
        self.assertTrue(bool(self.uuid_pattern.match(str(withdrawal.id))), "Should set the ID default on create")

    def test_to_dict(self):
        withdrawal = self.mixer.blend('transient.models.withdrawal.Withdrawal', payment_id=uuid.uuid4())
        withdrawal_dict = withdrawal.to_dict()
        self.assertTrue(bool(self.uuid_pattern.match(withdrawal_dict["id"])), "ID should be a string")
        self.assertEqual(str(withdrawal.payment_id), withdrawal_dict["payment_id"], "Payment ID should be a string")
        self.assertEqual(withdrawal.transaction_id, withdrawal_dict["transaction_id"])
        self.assertEqual(withdrawal.currency, withdrawal_dict["currency"])
        self.assertEqual(withdrawal.created_at, withdrawal_dict["created_at"])
        self.assertEqual(withdrawal.updated_at, withdrawal_dict["updated_at"])

    def test_by_payment(self):
        payment = self.mixer.blend('transient.models.payment.Payment')
        withdrawal = self.mixer.blend('transient.models.withdrawal.Withdrawal', payment_id=payment.id)
        self.session.add(payment)
        self.session.add(withdrawal)
        self.session.commit()
        payment_withdrawal = Withdrawal.by_payment(payment.id)
        self.assertEqual(payment_withdrawal.id, withdrawal.id)