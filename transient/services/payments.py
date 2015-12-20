import qrcode
from transient.models.payment import Payment, PaymentSchema
from transient.models.withdrawal import Withdrawal
from transient.lib.coind import CoindClient
from transient.services.webhooks import payment_status


def get_payment(id=None, **filters):
    if id:
        return Payment.query.get(id)
    else:
        return Payment.query.filter_by(**filters).first()


def get_payment_qrcode(payment):
    if not isinstance(payment, type(Payment)):
        payment = get_payment(payment)

    if not payment:
        raise ValueError("Invalid payment id")

    if payment.currency == "BTC":
        qr_data = "bitcoin:%s" % (payment.payment_address)
    elif payment.currency == "LTC":
        qr_data = "litecoin:%s" % (payment.payment_address)
    elif payment.currency == "DOGE":
        qr_data = "dogecoin:%s" % (payment.payment_address)
    else:
        qr_data = payment.payment_address

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    return qr.make_image()


def create_payment(**raw_data):
    # Get a rpc client for the payment currency type
    client = CoindClient(raw_data.get("currency"))

    # Parse the input payment data
    data, errors = PaymentSchema().load(raw_data)

    # Check if the merchant address is a valid crypto address
    valid_address = client.is_valid_address(data.get("merchant_address"))
    if not valid_address:
        raise ValueError("Invalid address")

    # Generate a new wallet address for this payment
    data["payment_address"] = client.create_address()

    payment = Payment(**data)
    return payment


def update_status(payment):
    if not isinstance(payment, type(Payment)):
        payment = get_payment(payment)

    current_status = payment.status
    new_status = current_status
    amount_received = payment.amount_received()
    amount_confirmed = payment.amount_confirmed()

    if amount_received == 0:
        new_status = "UNPAID"
    elif amount_received < payment.amount:
        new_status = "UNDERPAID"
    elif amount_received == payment.amount:
        new_status = "PAID"
        if amount_confirmed == amount_received:
            new_status = "CONFIRMED"

    status_changed = current_status != new_status

    if status_changed:
        payment.status = new_status
        payment_status(payment)
        if payment.status == "CONFIRMED":
            process_withdrawal(payment)

    return payment


def cancel_payment(payment, **options):
    raise NotImplementedError()


def process_overpayment(payment):
    raise NotImplementedError()


def process_withdrawal(payment):
    if not hasattr(payment, "id"):
        payment = get_payment(payment)

    if not payment:
        raise ValueError("Invalid payment id")

    # Check if a withdrawal already exists for this payment
    withdrawal = Withdrawal.by_payment(payment.id)
    if withdrawal:
        return withdrawal

    # Check the payment has been paid and confirmed
    is_paid = payment.amount_confirmed() == payment.amount
    if not is_paid:
        raise ValueError("Payment has not been confirmed")

    # Get a RPC client for the payment currency type
    client = CoindClient(payment.currency)

    # Send the payment to the merchant
    transaction_id = client.send(payment.merchant_address, payment.amount)

    # Create the withdrawal record
    withdrawal_data = dict(payment_id=payment.id, transaction_id=transaction_id)
    withdrawal = Withdrawal.from_dict(withdrawal_data)

    return withdrawal
