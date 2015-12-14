import re
from decimal import Decimal
import six
from transient.test.unit import BaseTestCase
from transient.models.payment import Payment, validate_amount


class TestPaymentModel(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    def test_defaults(self):
        payment = Payment()
        self.assertTrue(bool(self.uuid_pattern.match(str(payment.id))))
        self.assertEqual(payment.status, "UNPAID")
        self.assertEqual(payment.confirmations_required, 2)

    def test_to_dict(self):
        payment = self.mixer.blend('transient.models.payment.Payment')
        payment_dict = payment.to_dict()
        self.assertTrue(bool(self.uuid_pattern.match(payment_dict["id"])))
        self.assertTrue("amount_received" in payment_dict)
        self.assertTrue("amount_confirmed" in payment_dict)
        self.assertIsInstance("amount_received", six.string_types)
        self.assertIsInstance("amount_confirmed", six.string_types)
        self.assertTrue("transactions" in payment_dict)
        self.assertFalse("merchant_address" in payment_dict)
        self.assertFalse("confirmations_required" in payment_dict)
        self.assertEqual(str(payment.amount), payment_dict["amount"])
        self.assertEqual(payment.currency, payment_dict["currency"])
        self.assertEqual(payment.status, payment_dict["status"])
        self.assertEqual(payment.created_at, payment_dict["created_at"])
        self.assertEqual(payment.updated_at, payment_dict["updated_at"])
        self.assertEqual(payment.expires_at, payment_dict["expires_at"])

    def test_validate_amount(self):
        cases = [
            (10, True),
            (Decimal("10"), True),
            (Decimal("-10"), False),
            (Decimal("-0.000009"), False),
            (Decimal("99999999.99999999"), True),
            (Decimal("9999999999999999"), False),
            ("potato", False)
        ]
        for case in cases:
            if case[1]:
                self.assertEqual(validate_amount(case[0]), case[0])
            else:
                self.assertRaises(ValueError, validate_amount, case[0])

    def test_amount_received(self):
        Transaction = 'transient.models.transaction.Transaction'
        payment = self.mixer.blend('transient.models.payment.Payment')

        payment.transactions = []
        self.assertEqual(payment.amount_received(), Decimal("0"))

        payment.transactions = [self.mixer.blend(Transaction, amount=Decimal("10"))]
        self.assertEqual(payment.amount_received(), Decimal("10"))

        payment.transactions = [
            self.mixer.blend(Transaction, amount=Decimal("0")),
            self.mixer.blend(Transaction, amount=Decimal("5")),
            self.mixer.blend(Transaction, amount=Decimal("10"))
        ]
        self.assertEqual(payment.amount_received(), Decimal("15"))

        payment.transactions = [
            self.mixer.blend(Transaction, amount=Decimal("0")),
            self.mixer.blend(Transaction, amount=Decimal("999.999"))
        ]
        self.assertEqual(payment.amount_received(), Decimal("999.999"))

    def test_amount_confirmed(self):
        Transaction = 'transient.models.transaction.Transaction'
        payment = self.mixer.blend('transient.models.payment.Payment', confirmations_required=2)

        payment.transactions = []
        self.assertEqual(payment.amount_confirmed(), Decimal("0"))

        payment.transactions = [self.mixer.blend(Transaction, amount=Decimal("10"), confirmations=1)]
        self.assertEqual(payment.amount_confirmed(), Decimal("0"))

        payment.transactions = [self.mixer.blend(Transaction, amount=Decimal("10"), confirmations=2)]
        self.assertEqual(payment.amount_confirmed(), Decimal("10"))

        payment.transactions = [
            self.mixer.blend(Transaction, amount=Decimal("100"), confirmations=0),
            self.mixer.blend(Transaction, amount=Decimal("999.999"), confirmations=10)
        ]
        self.assertEqual(payment.amount_confirmed(), Decimal("999.999"))
