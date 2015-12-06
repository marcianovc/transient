from transient.lib.database import session
from transient.lib.crypto import get_client
from transient.models.payment import Payment, payment_schema


def get_payment(id, **options):
    pass


def get_payment_qrcode(id, **options):
    import qrcode
    payment = Payment.query.get(id)

    if not payment:
        raise ValueError("Invalid payment id")

    if payment.currency == "DOGE":
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


def create_payment(**data):
    if not data["currency"]:
        raise ValueError("Currency is required")
    else:
        data["currency"] = data["currency"].upper()

    # Use the address file as payee_address if provided,
    # this just makes the api a bit cleaner.
    if data["address"]:
        data["payee_address"] = data["address"]
        del data["address"]

    # Get a rpc client for the payment currency type
    client = get_client(data["currency"])

    # Check if the payee address is a valid crypto address
    if not client.is_valid_address(data["payee_address"]):
        raise ValueError("Invalid address")

    # Generate a new wallet address for this payment
    data["payment_address"] = client.create_address()

    # Parse the data dict, then create and save a payment model
    schema_data, errors = payment_schema.load(data)
    payment = Payment(**schema_data)
    session.add(payment)
    session.commit()

    return payment
