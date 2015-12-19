import re
from decimal import Decimal
from mock import patch
from dogecoinrpc.data import TransactionInfo
from transient.test.unit import BaseTestCase
from transient.services.transactions import *


class TestTransactionsService(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    def _make_transaction_info(self, transaction_id, payment=None, **overrides):
        transaction_data = {
            "txid": transaction_id,
            "category": "receive",
            "address": payment.payment_address if payment else "DHqFuLmMUSu2wzEMmpa3CDocwmbWQU49zx",
            "account": "lorem ipsum",
            "amount": Decimal("12345.12345"),
            "fee": 1,
            "confirmations": 0
        }
        if overrides:
            transaction_data.update(overrides)
        return TransactionInfo(**transaction_data)

    @patch("transient.services.transactions.Transaction")
    def test_get_transaction(self, transaction_mock):
        transaction = self.mixer.blend(transaction_mock)
        get_transaction(transaction.id)
        transaction_mock.query.get.assert_called_with(transaction.id)

    @patch("transient.services.transactions.Transaction")
    def test_get_transaction_using_filter(self, transaction_mock):
        transaction_id = "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"
        get_transaction(transaction_id=transaction_id)
        transaction_mock.query.filter_by.assert_called_with(transaction_id=transaction_id)

    def test_get_unconfirmed(self):
        Payment = "transient.models.payment.Payment"
        Transaction = "transient.models.transaction.Transaction"
        payment = self.mixer.blend(Payment, confirmations_required=2)
        doge_transaction = self.mixer.blend(Transaction, payment_id=payment.id, currency="DOGE", confirmations=1)
        doge_transaction_2 = self.mixer.blend(Transaction, payment_id=payment.id, currency="DOGE", confirmations=0)
        btc_transaction = self.mixer.blend(Transaction, payment_id=payment.id, currency="BTC", confirmations=1)
        confirmed_transaction = self.mixer.blend(Transaction, payment_id=payment.id, currency="DOGE", confirmations=3)
        self.session.add(payment)
        self.session.add(doge_transaction)
        self.session.add(doge_transaction_2)
        self.session.add(btc_transaction)
        self.session.add(confirmed_transaction)
        self.session.commit()
        result = get_unconfirmed("DOGE")
        self.assertIn(doge_transaction, result, "Did not include an unconfirmed transaction")
        self.assertIn(doge_transaction, result, "Did not include an unconfirmed transaction")
        self.assertNotIn(btc_transaction, result, "Should not include a transaction of a different currency")
        self.assertNotIn(confirmed_transaction, result, "Should not include a confirmed transaction")

    @patch("transient.services.transactions.CoindClient")
    @patch("transient.services.transactions.payments")
    def test_create_transaction(self, payments_mock, coind_mock):
        payment = self.mixer.blend("transient.models.payment.Payment", transactions=[])
        data = {
            "currency": "DOGE",
            "transaction": "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"
        }
        transaction_info = self._make_transaction_info(data["transaction"], payment)

        payments_mock.get_payment.return_value = payment
        payments_mock.update_status.return_value = payment
        coind_instance_mock = coind_mock.return_value
        coind_instance_mock.get_transaction.return_value = transaction_info

        transaction = create_transaction(**data)
        self.assertTrue(bool(self.uuid_pattern.match(str(transaction.id))), "Did not create a valid UUID.")
        self.assertEqual(transaction.currency, data["currency"])
        self.assertEqual(transaction.transaction_id, data["transaction"])
        self.assertEqual(transaction.confirmations, 0)
        self.assertEqual(transaction.amount, transaction_info.amount)
        self.assertEqual(transaction.fee, transaction_info.fee)
        self.assertTrue(hasattr(transaction, "created_at"))
        self.assertTrue(hasattr(transaction, "updated_at"))
        payments_mock.update_status.assert_called_with(payment)

    @patch("transient.services.transactions.CoindClient")
    @patch("transient.services.transactions.payments")
    @patch('transient.services.transactions.get_transaction')
    def test_create_transaction_with_existing_payment_updates_conformations_count(self, get_transaction_mock,
                                                                                  payments_mock, coind_mock):
        transaction_id = "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"
        transaction = self.mixer.blend('transient.models.transaction.Transaction', transaction_id=transaction_id,
                                       confirmations=0)
        payment = self.mixer.blend("transient.models.payment.Payment", transactions=[transaction])
        data = {
            "currency": "DOGE",
            "transaction": transaction_id
        }
        transaction_info = self._make_transaction_info(transaction_id, payment, confirmations=0)

        get_transaction_mock.return_value = transaction
        payments_mock.get_payment.return_value = payment
        payments_mock.update_status.return_value = payment
        coind_instance_mock = coind_mock.return_value
        coind_instance_mock.get_transaction.return_value = transaction_info

        transaction_info.confirmations = 1
        transaction_2 = create_transaction(**data)
        self.assertEqual(transaction_2.confirmations, 1, "Did not update the confirmations count.")
        self.assertEqual(transaction_2.id, transaction.id, "Created a new transaction instead of updating existing "
                                                           "transaction's confirmations.")

        transaction_info.confirmations = 0
        transaction_3 = create_transaction(**data)
        self.assertEqual(transaction_3.confirmations, 0)
        self.assertEqual(transaction_3.id, transaction.id, "Created a new transaction instead of updating existing "
                                                           "transaction's confirmations.")

    @patch("transient.services.transactions.CoindClient")
    @patch("transient.services.transactions.payments")
    @patch('transient.services.transactions.get_unconfirmed')
    @patch('transient.services.transactions.get_transaction')
    def test_update_unconfirmed_transactions(self, get_transaction_mock, get_unconfirmed_mock, payments_mock,
                                             coind_mock):
        Payment = "transient.models.payment.Payment"
        Transaction = "transient.models.transaction.Transaction"
        payment_1 = self.mixer.blend(Payment, confirmations_required=2)
        payment_2 = self.mixer.blend(Payment, confirmations_required=2)
        transaction_1 = self.mixer.blend(Transaction, payment_id=payment_1.id, currency="DOGE", confirmations=1)
        transaction_2 = self.mixer.blend(Transaction, payment_id=payment_2.id, currency="DOGE", confirmations=0)
        transaction_3 = self.mixer.blend(Transaction, payment_id=payment_2.id, currency="DOGE", confirmations=3)
        transaction_info_1 = self._make_transaction_info(transaction_1.transaction_id, payment_1, confirmations=2)
        transaction_info_2 = self._make_transaction_info(transaction_2.transaction_id, payment_2, confirmations=1)

        get_unconfirmed_mock.return_value = [transaction_1, transaction_2]
        coind_instance_mock = coind_mock.return_value
        coind_instance_mock.get_transaction.side_effect = [transaction_info_1, transaction_info_2]

        updated_transactions = update_unconfirmed_transactions("DOGE")

        self.assertIn(transaction_1, updated_transactions, "Did not return an updated transaction")
        self.assertIn(transaction_2, updated_transactions, "Did not return an updated transaction")
        self.assertNotIn(transaction_3, updated_transactions, "Returned a transaction that did not update")
        self.assertEqual(transaction_1.confirmations, 2)
        self.assertEqual(transaction_2.confirmations, 1)
        self.assertEqual(payments_mock.update_status.call_count, 2)
        payments_mock.update_status.assert_any_call(payment_1.id)
        payments_mock.update_status.assert_any_call(payment_2.id)
