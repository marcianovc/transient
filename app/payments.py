from app.database import db_session
from app.crypto import DogecoinClient
from app.models import *


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


def create_payment(data, dump=False):
    if not data["currency"]:
        raise ValueError("Currency is required")
    else:
        data["currency"] = data["currency"].upper()

    # Use the address file ad payee_address if provided,
    # this just makes the api a bit cleaner.
    if data["address"]:
        data["payee_address"] = data["address"]
        del data["address"]

    # Get a rpc client for the payment currency type
    client = get_crypto_client(data["currency"])

    # Check if the payee address is a valid crypto address
    if not client.is_valid_address(data["payee_address"]):
        raise ValueError("Invalid address")

    # Generate a new wallet address for this payement
    data["payment_address"] = client.get_new_address()

    # Parse the data dict, then create and save a payment model
    schema_data, errors = payment_schema.load(data)
    payment = Payment(**schema_data)
    db_session.add(payment)
    db_session.commit()

    if dump:
        transactions = payment.transactions
        payment_result = payment_schema.dump(payment)
        transactions_result = transactions_schema.dump(transactions)
        payment_data = payment_result.data
        payment_data["transactions"] = transactions_result.data
        return payment_data
    else:
        return payment


def create_transaction(data, dump=False):
    # TODO: if we already had the transaction recorded, we can just update the confirmations

    if not data["currency"]:
        raise ValueError("Currency is required")
    else:
        data["currency"] = data["currency"].upper()

    if not data["transaction_id"]:
        raise ValueError("Transaction ID is required")

    # Get a rpc client for the payment currency type
    client = get_crypto_client(data["currency"])

    # Get the transaction data
    transaction_data = client.get_transaction(data["transaction_id"])
    data.update({
        "amount": transaction_data["amount"],
        "fee": transaction_data["fee"],
        "confirmations": transaction_data["confirmations"],
        "category": transaction_data["category"],
        "sent_at": transaction_data["date"]
    })

    # Find the payment associated with the receiving address
    payment = Payment.query.filter(Payment.payment_address == transaction_data["address"]).first()

    # We don"t have a payment that is waiting for transactions to this address
    if not payment:
        return None

    data.payment_id = payment.id

    schema_data, errors = transaction_schema.load(data)
    transaction = Transaction(**schema_data)
    db_session.add(transaction)
    db_session.commit()

    if dump:
        return transaction_schema.dump(transaction).data
    else:
        return transaction


def get_crypto_client(currency):
    if currency == "DOGE":
        return DogecoinClient()
    else:
        raise ValueError("Invalid currency or currency not yet supported")
