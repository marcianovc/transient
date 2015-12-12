from decimal import Decimal
from transient.test.unit import BaseTestCase
from mock import patch
from transient.services.transactions import *
from dogecoinrpc.data import TransactionInfo
import re


class TestTransactionsService(BaseTestCase):

    uuid_pattern = re.compile("(\w{8}(-\w{4}){3}-\w{12}?)")

    @patch("transient.services.transactions.CryptocurrencyClient")
    @patch("transient.services.transactions.payments")
    def test_create_transaction(self, mock_payments, mock_client):
        payment = self.mixer.blend("transient.models.payment.Payment", transactions=[])
        data = {
            "currency": "DOGE",
            "transaction": "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"
        }
        transaction_data = {
            "txid": data["transaction"],
            "category": "receive",
            "address": payment.payment_address,
            "account": "lorem ipsum",
            "amount": Decimal("12345"),
            "fee": 1,
            "confirmations": 0
        }

        mock_payments.get_payment.return_value = payment
        mock_payments.update_status.return_value = payment
        mock_client_instance = mock_client.return_value
        transaction_info = TransactionInfo(**transaction_data)
        mock_client_instance.get_transaction.return_value = transaction_info

        transaction = create_transaction(**data)
        self.assertTrue(bool(self.uuid_pattern.match(str(transaction.id))))
        self.assertEqual(transaction.currency, data["currency"])
        self.assertEqual(transaction.transaction_id, data["transaction"])
        self.assertEqual(transaction.confirmations, 0)
        self.assertEqual(transaction.amount, transaction_data["amount"])
        self.assertEqual(transaction.fee, transaction_data["fee"])
        self.assertTrue(hasattr(transaction, "created_at"))
        self.assertTrue(hasattr(transaction, "updated_at"))
        mock_payments.update_status.assert_called_with(payment)

    def test_create_transaction_with_existing_payment_updates_conformations(self):
        pass
