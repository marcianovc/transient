import json
from decimal import Decimal
from dogecoinrpc.data import TransactionInfo
from mock import patch
from transient.test.integration import BaseIntegrationTest


class TestAPI(BaseIntegrationTest):

    def test_ping(self):
        r = self.client.get("/ping")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, "pong")

    @patch('transient.services.payments.CoindClient')
    def test_post_payment(self, coind_mock):
        coind_mock.return_value.is_valid_address.return_value = True
        coind_mock.return_value.create_address.return_value = "D5Km7yuVkJnPGWHf2UfvNMxLDwGsMDn9ya"

        payload = dict(currency="DOGE", amount="999.999", address="DGMJjZjgdGDmgk21PARUajeUpGNrpq6kph")
        r = self.client.post("/payments", content_type="application/json", data=json.dumps(payload))

        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])

        payment = r.json["payment"]
        response_fields = ["id", "amount_confirmed", "amount_received", "currency", "amount", "payment_address",
                           "status", "created_at"]

        self.assertEqual(payment.keys().sort(), response_fields.sort())
        self.assertEqual(payment["amount"], payload["amount"])
        self.assertEqual(payment["currency"], payload["currency"])
        self.assertEqual(payment["status"], "UNPAID")

    @patch('transient.services.transactions.CoindClient')
    def test_post_transaction(self, coind_mock):
        transaction_id = "ac3b07ac490b76b7d3f845e0593030e48ac44032ba8e3690a4e5f2e09416ed76"
        payment_address = "D5Km7yuVkJnPGWHf2UfvNMxLDwGsMDn9ya"

        coind_mock.return_value.get_transaction.return_value = TransactionInfo(**{
            "txid": transaction_id,
            "address": payment_address,
            "category": "receive",
            "account": "lorem ipsum",
            "amount": Decimal("10"),
            "fee": 1,
            "confirmations": 0
        })

        payload = dict(currency="DOGE", transaction=transaction_id)
        r = self.client.post("/transactions", content_type="application/json", data=json.dumps(payload))
        transaction = r.json["transaction"]

        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["success"])
        self.assertEqual(transaction["transaction_id"], transaction_id)
        self.assertEqual(transaction["amount"], "10")
        self.assertEqual(transaction["currency"], payload["currency"])
        self.assertEqual(transaction["confirmations"], 0)
        self.assertEqual(transaction["fee"], "1")
