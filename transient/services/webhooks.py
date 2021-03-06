import requests
from transient import settings


def payment_status(payment):
    if not payment:
        raise ValueError("Payment object is required")
    webhook_url = settings.PAYMENT_WEBHOOK_URL
    if not webhook_url:
        return
    payload = payment.to_dict(("id", "status", "amount_received", "amount_confirmed"))
    r = requests.post(url=webhook_url, json=payload)
    if r.status_code != requests.codes.ok:
        # TODO: Handle a webhook error, maybe send again at a later date...
        pass
