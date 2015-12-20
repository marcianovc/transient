import re
from decimal import Decimal
from mock import patch, mock
from transient.test.unit import BaseTestCase
from transient.services.payments import *


class TestPaymentsService(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    @patch("transient.services.payments.Payment")
    def test_get_payment(self, payment_mock):
        mixer_payment = self.mixer.blend("transient.models.payment.Payment", transactions=[])
        payment_mock.query.get.return_value = mixer_payment
        payment = get_payment(mixer_payment.id)
        payment_mock.query.get.assert_called_with(mixer_payment.id)
        self.assertEqual(payment.id, mixer_payment.id)

    @patch("transient.services.payments.Payment")
    @patch('transient.services.payments.get_payment')
    @patch("transient.services.payments.qrcode.QRCode")
    def test_get_payment_qrcode(self, qrcode_mock, get_payment_mock, payment_mock):
        payment = self.mixer.blend(payment_mock)
        get_payment_mock.return_value = payment
        qrcode_mock_instance = qrcode_mock.return_value
        cases = [
            ("BTC", "bitcoin:%s" % payment.payment_address),
            ("LTC", "litecoin:%s" % payment.payment_address),
            ("DOGE", "dogecoin:%s" % payment.payment_address),
            ("INVALID", payment.payment_address)
        ]
        for case in cases:
            payment.currency = case[0]
            get_payment_qrcode(payment.id)
            qrcode_mock_instance.make_image.assert_called_once_with()
            qrcode_mock_instance.add_data.assert_called_once_with(case[1])
            qrcode_mock.reset_mock()

    @patch("transient.services.payments.CoindClient")
    def test_create_payment(self, client_mock):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE",
            "amount": 10
        }
        mock_client_instance = client_mock.return_value
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
    def test_create_payment_with_invalid_address(self, client_mock):
        data = {
            "address": "invalidaddress"
        }
        client_mock.return_value.is_valid_address.return_value = False
        self.assertRaises(ValueError, create_payment, **data)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment_with_extreme_amounts(self, client_mock):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE"
        }
        amounts = (Decimal("99999999.99999999"), Decimal("0.00000001"), Decimal("90000000"))

        mock_client_instance = client_mock.return_value
        mock_client_instance.create_address.return_value = "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx"
        mock_client_instance.is_valid_address.return_value = True

        for amount in amounts:
            data["amount"] = amount
            payment = create_payment(**data)
            self.assertEqual(payment.amount, amount)

    @patch("transient.services.payments.CoindClient")
    def test_create_payment_with_invalid_amount_raises_exception(self, client_mock):
        data = {
            "address": "DFq66AjLeoJTtpHo47fg3rYrUydZxcANLN",
            "currency": "DOGE"
        }
        amounts = (Decimal("999999999999"), Decimal("-10"), Decimal("-0.1"), "potato")

        mock_client_instance = client_mock.return_value
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

        payment = self.mixer.blend(payment_mock, min_confirmations=0, status="UNPAID")
        get_payment_mock.return_value = payment
        payment_status_mock.return_value = None

        for case in cases:
            payment.amount = case[0]
            payment.amount_received.return_value = case[1]
            payment = update_status(payment)
            self.assertEqual(payment.status, case[2])

    @patch('transient.services.payments.Payment')
    @patch('transient.services.payments.get_payment')
    @patch('transient.services.payments.payment_status')
    @patch('transient.services.payments.process_withdrawal')
    def test_update_status_on_amount_confirmed(self, process_withdrawal_mock, payment_status_mock, get_payment_mock,
                                               payment_mock):
        # Amount, Amount received, Min confirmations, Confirmations, Expected status
        cases = [
            (10, 10, 0, "PAID"),
            (10, 10, 5, "PAID"),
            (10, 5, 5, "UNDERPAID"),
            (10, 10, 10, "CONFIRMED"),
            (Decimal("0.1"), Decimal("0.1"), Decimal("0.1"), "CONFIRMED"),
            (Decimal("99999.99999"), Decimal("99999.99999"), Decimal("99999.99999"), "CONFIRMED")
        ]

        payment = self.mixer.blend(payment_mock, status="UNPAID")
        get_payment_mock.return_value = payment
        payment_status_mock.return_value = None
        process_withdrawal.return_value = True

        for case in cases:
            payment.status = "UNPAID"
            payment.amount = case[0]
            payment.amount_received.return_value = case[1]
            payment.amount_confirmed.return_value = case[2]
            payment = update_status(payment)
            self.assertEqual(payment.status, case[3])
            if case[3] == "CONFIRMED":
                process_withdrawal_mock.assert_called_once_with(payment)
                process_withdrawal_mock.reset_mock()

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

        payment = self.mixer.blend(payment_mock, min_confirmations=0)
        payment_status_mock.return_value = None
        get_payment_mock.return_value = payment

        for case in cases:
            payment.status = case[2]
            payment.amount = case[0]
            payment.amount_received.return_value = case[1]
            payment = update_status(payment)
            self.assertEqual(payment.status, case[3])
            if case[4]:
                payment_status_mock.assert_called_once_with(payment)
            payment_status_mock.reset_mock()

    @patch("transient.services.payments.CoindClient")
    def test_process_withdrawal(self, client_mock):
        amount = Decimal("10")
        transaction_id = "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"

        client_instance_mock = client_mock.return_value
        client_instance_mock.send.return_value = transaction_id

        payment = self.mixer.blend("transient.models.payment.Payment", amount=amount, confirmations_required=0,
                                   merchant_address="DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx")

        payment.amount_confirmed = mock.Mock(return_value=amount)

        withdrawal = process_withdrawal(payment)

        self.assertTrue(bool(self.uuid_pattern.match(str(withdrawal.id))))
        self.assertEqual(withdrawal.transaction_id, transaction_id, "Did not save the transaction ID")
        client_instance_mock.send.assert_called_once_with(payment.merchant_address, payment.amount)

        payment.amount_confirmed.return_value = Decimal("5")
        self.assertRaises(ValueError, process_withdrawal, payment)

    @patch('transient.services.payments.Withdrawal')
    def test_process_withdrawal_only_creates_one_withdrawal(self, withdrawal_mock):
        payment = self.mixer.blend("transient.models.payment.Payment")
        withdrawal = self.mixer.blend("transient.models.withdrawal.Withdrawal", payment_id=payment.id)
        withdrawal_mock.by_payment = mock.Mock(return_value=withdrawal)
        new_withdrawal = process_withdrawal(payment)
        self.assertEqual(new_withdrawal.id, withdrawal.id)
