from decimal import Decimal
from transient.test.unit import BaseTestCase
from mock import patch
from transient.services.payments import *
import re


class TestPaymentsService(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    @patch("transient.services.payments.Payment")
    def test_get_payment(self, payment_mock):
        mixer_payment = self.mixer.blend("transient.models.payment.Payment", transactions=[])
        payment_mock.query.get.return_value = mixer_payment
        payment = get_payment(mixer_payment.id)
        payment_mock.query.get.assert_called_with(mixer_payment.id)
        self.assertEqual(payment.id, mixer_payment.id)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment(self, mock_client):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE",
            "amount": 10
        }
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_address.return_value = "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx"
        mock_client_instance.is_valid_address.return_value = True
        payment = create_payment(**data)
        self.assertTrue(bool(self.uuid_pattern.match(str(payment.id))))
        self.assertEqual(payment.merchant_address, data["address"])
        self.assertEqual(payment.amount, data["amount"])
        self.assertEqual(payment.currency, data["currency"])
        self.assertEqual(payment.status, "UNPAID")
        self.assertTrue(hasattr(payment, "merchant_address"))
        self.assertTrue(hasattr(payment, "created_at"))
        self.assertTrue(hasattr(payment, "updated_at"))
        self.assertEqual(payment.expires_at, None)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment_with_invalid_address(self, mock_client):
        data = {
            "address": "invalidaddress"
        }
        mock_client.return_value.is_valid_address.return_value = False
        self.assertRaises(ValueError, create_payment, **data)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment_with_extreme_amounts(self, mock_client):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE"
        }
        amounts = (Decimal("99999999.99999999"), Decimal("0.00000001"), Decimal("90000000"))

        mock_client_instance = mock_client.return_value
        mock_client_instance.create_address.return_value = "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx"
        mock_client_instance.is_valid_address.return_value = True

        for amount in amounts:
            data["amount"] = amount
            payment = create_payment(**data)
            self.assertEqual(payment.amount, amount)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment_with_invalid_amount_raises_exception(self, mock_client):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE"
        }
        amounts = (Decimal("999999999999"), Decimal("-10"), Decimal("-0.1"), "potato")

        mock_client_instance = mock_client.return_value
        mock_client_instance.create_address.return_value = "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx"
        mock_client_instance.is_valid_address.return_value = True

        for amount in amounts:
            data["amount"] = amount
            self.assertRaises(ValueError, create_payment, **data)

    def test_create_payment_with_invalid_currency(self):
        data = {
            "currency": "INVALID"
        }
        self.assertRaises(ValueError, create_payment, **data)

    @patch('transient.services.payments.Payment')
    @patch('transient.services.payments.get_payment')
    @patch('transient.services.payments.payment_status')
    def test_update_status_on_amount_received(self, payment_status_mock, get_payment_mock, payment_mock):
        # Amount, Amount received, Expected status
        cases = [
            (10, 0, "UNPAID"),
            (Decimal("0.1"), Decimal("0"), "UNPAID"),
            (10, 10, "PAID"),
            (Decimal("99999.99999"), Decimal("99999.99999"), "PAID"),
            (10, 5, "UNDERPAID"),
            (Decimal("99999.99999"), Decimal("99999.88888"), "UNDERPAID")
        ]

        paid_payment = self.mixer.blend(payment_mock, min_confirmations=0, status="UNPAID")
        get_payment_mock.return_value = paid_payment
        payment_status_mock.return_value = None

        for case in cases:
            paid_payment.amount = case[0]
            paid_payment.amount_received.return_value = case[1]
            payment = update_status(paid_payment)
            self.assertEqual(payment.status, case[2])

    @patch('transient.services.payments.Payment')
    @patch('transient.services.payments.get_payment')
    @patch('transient.services.payments.payment_status')
    def test_update_status_on_amount_confirmed(self, payment_status_mock, get_payment_mock, payment_mock):
        # Amount, Amount received, Min confirmations, Confirmations, Expected status
        cases = [
            (10, 10, 0, "PAID"),
            (10, 10, 5, "PAID"),
            (10, 5, 5, "UNDERPAID"),
            (10, 10, 10, "CONFIRMED"),
            (Decimal("0.1"), Decimal("0.1"), Decimal("0.1"), "CONFIRMED"),
            (Decimal("99999.99999"), Decimal("99999.99999"), Decimal("99999.99999"), "CONFIRMED")
        ]

        paid_payment = self.mixer.blend(payment_mock, status="UNPAID")
        get_payment_mock.return_value = paid_payment
        payment_status_mock.return_value = None

        for case in cases:
            paid_payment.amount = case[0]
            paid_payment.amount_received.return_value = case[1]
            paid_payment.amount_confirmed.return_value = case[2]
            payment = update_status(paid_payment)
            self.assertEqual(payment.status, case[3])

    @patch('transient.services.payments.Payment')
    @patch('transient.services.payments.get_payment')
    @patch('transient.services.payments.payment_status')
    def test_update_status_sends_webhook_notification(self, payment_status_mock, get_payment_mock, payment_mock):
        # Amount, Amount received, From status, To status, Send notification
        cases = [
            (10, 0, "UNPAID", "UNPAID", False),
            (10, 5, "UNPAID", "UNDERPAID", True),
            (10, 10, "UNPAID", "PAID", True),
            (10, 5, "UNDERPAID", "UNDERPAID", False),
            (10, 10, "UNDERPAID", "PAID", True),
            (10, 10, "PAID", "PAID", False)
        ]

        paid_payment = self.mixer.blend(payment_mock, min_confirmations=0)
        payment_status_mock.return_value = None
        get_payment_mock.return_value = paid_payment

        for case in cases:
            payment_status_mock.called = False
            paid_payment.status = case[2]
            paid_payment.amount = case[0]
            paid_payment.amount_received.return_value = case[1]
            payment = update_status(paid_payment)
            self.assertEqual(payment.status, case[3])
            self.assertEqual(payment_status_mock.called, case[4])
