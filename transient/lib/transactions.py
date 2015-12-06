from transient.lib.database import session
from transient.lib.crypto import get_client
from transient.models.payment import Payment
from transient.models.transaction import Transaction, transaction_schema


def create_transaction(**data):
    # TODO: if we already had the transaction recorded, we can just update the confirmations

    if not data["currency"]:
        raise ValueError("Currency is required")
    else:
        data["currency"] = data["currency"].upper()

    if not data["transaction_id"]:
        raise ValueError("Transaction ID is required")

    # Get a rpc client for the payment currency type
    client = get_client(data["currency"])

    # Get the transaction data
    transaction_data = client.get_transaction(data["transaction_id"])
    data.update({
        "amount": transaction_data.amount,
        "fee": transaction_data.fee,
        "confirmations": transaction_data.confirmations,
        "category": transaction_data.category
    })

    # Find the payment associated with the receiving address
    payment = Payment.by_address(transaction_data.address)

    # If we have a payment for this address, store a reference to the payment
    if payment:
        data["payment_id"] = payment.id

    schema_data, errors = transaction_schema.load(data)
    transaction = Transaction(**schema_data)
    session.add(transaction)
    session.commit()

    return transaction
