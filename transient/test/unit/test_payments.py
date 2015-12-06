from transient.test.unit import BaseTestCase
import re
from decimal import Decimal
from transient.lib.payments import create_payment


class PaymentsTest(BaseTestCase):

    valid_dogecoin_address = "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN"
    invalid_dogecoin_address = "thisisnotavalidaddress"

    def make_payment(self, overrides={}):
        data = {
            "address": self.valid_dogecoin_address,
            "currency": "DOGE",
            "amount": 10
        }
        if overrides:
            data.update(overrides)
        return data

    def test_create_valid_payment(self):
        payment_data = self.make_payment()
        payment = create_payment(**payment_data)
        id_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")
        self.assertTrue(bool(id_pattern.match(str(payment.id))))
        self.assertEqual(payment.payee_address, payment_data["address"])
        self.assertEqual(payment.amount, payment_data["amount"])
        self.assertEqual(payment.currency, payment_data["currency"])
        self.assertEqual(payment.status, "UNPAID")
        self.assertTrue(hasattr(payment, "payee_address"))
        self.assertTrue(hasattr(payment, "amount_received"))
        self.assertTrue(hasattr(payment, "created_at"))
        self.assertTrue(hasattr(payment, "updated_at"))
        self.assertEqual(payment.created_at, payment.updated_at)
        self.assertEqual(payment.expires_at, None)

    def test_create_large_payment(self):
        payment = create_payment(**self.make_payment({
            "amount": 99999999.99999999
        }))
        self.assertEqual(payment.amount, Decimal("99999999.99999999"))

    def test_create_small_payment(self):
        payment = create_payment(**self.make_payment({
            "amount": 0.00000001
        }))
        self.assertEqual(payment.amount, Decimal("0.00000001"))

    def test_create_payment_with_invalid_currency(self):
        self.assertRaises(ValueError, create_payment, **self.make_payment({
            "currency": "INVALID"
        }))

    def test_create_payment_with_invalid_address(self):
        self.assertRaises(ValueError, create_payment, **self.make_payment({
            "address": self.invalid_dogecoin_address
        }))

    def test_create_payment_with_invalid_amount(self):
        self.assertRaises(ValueError, create_payment, **self.make_payment({
            "amount": -999
        }))

    def test_create_valid_qrcode(self):
        self.assertEqual(True, False)
