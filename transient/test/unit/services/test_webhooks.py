from os import environ
from mock import patch
from requests import Response
from transient.test.unit import BaseTestCase
from transient.services.webhooks import *


class TestWebhookService(BaseTestCase):

    @patch('transient.services.webhooks.requests')
    def test_payment_status_webhook(self, requests_mock):
        webhook_url = "http://example.com/webhook"
        environ["PAYMENT_WEBHOOK_URL"] = webhook_url
        response = Response()
        response.status_code = 200
        requests_mock.post.return_value = response
        payment = self.mixer.blend('transient.models.payment.Payment')
        payment_status(payment)
        args, kwargs = requests_mock.post.call_args
        self.assertTrue(requests_mock.post.called, "Did not call webhook URL")
        self.assertEqual(kwargs["url"], webhook_url)
        self.assertEqual(kwargs["json"].keys().sort(), ["id", "status", "amount_received", "amount_confirmed"].sort(),
                         "Webhook URL was sent the wrong data")

    @patch('transient.services.webhooks.requests')
    def test_payment_status_webhook_without_url(self, requests_mock):
        environ["PAYMENT_WEBHOOK_URL"] = ""
        payment = self.mixer.blend('transient.models.payment.Payment')
        payment_status(payment)
        self.assertFalse(requests_mock.post.called, "Webhook URL was called, but it did not exist")

    def test_payment_status_webhook_without_payment(self):
        self.assertRaises(ValueError, payment_status, None)
