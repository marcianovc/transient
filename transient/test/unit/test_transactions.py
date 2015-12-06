from transient.test.unit import BaseTestCase
from mock import patch, MagicMock
from dogecoinrpc.data import TransactionInfo
from transient.lib.transactions import create_transaction

class TransactionsTest(BaseTestCase):

    def setUp(self):
        super(TransactionsTest, self).setUp()
        from transient.models.payment import Payment
        from transient.models.transaction import Transaction
        Transaction.query.delete()
        Payment.query.delete()
        self.session.commit()

    def make_transaction(self, overrides={}):
        data = {
            "txid": "8fa6814ca4dd216270c659d792a86ae15360b34165579f02b8740ea1a6d5a4c2",
            "address": "DB3Na2iTbkfFWaadT45ykyoTJHL3DfbmZ9",
            "category": "receive",
            "amount": 2,
            "fee": 1,
            "confirmations": 0
        }
        if overrides:
            data.update(overrides)
        return data

    @patch("transient.lib.crypto.CryptocurrencyClient")
    @patch("transient.lib.crypto.DogecoinClient")
    def test_create_new_transaction(self, DogecoinClientMock, CryptocurrencyClientMock):
        transaction_data = self.make_transaction()
        self.mixer.blend('transient.models.payment.Payment', payment_address=transaction_data["address"],
                         transactions=[])

        DogecoinClientMockInstance = DogecoinClientMock.return_value
        DogecoinClientMockInstance.get_client = MagicMock(return_value=True)
        DogecoinClientMockInstance.get_transaction = MagicMock(return_value=TransactionInfo(**transaction_data))

        transaction = create_transaction(**{
            "currency": "DOGE",
            "transaction_id": transaction_data["txid"]
        })

        self.assertEqual(transaction.transaction_id, transaction_data["txid"])
