from transient.models.transaction import Transaction, TransactionSchema
from transient.services import payments
from transient.lib.crypto import CryptocurrencyClient


def create_transaction(**data):
    if not data["transaction"]:
        raise ValueError("Transaction ID is required")

    # If we already had the transaction recorded, we can just update the confirmations
    # TODO

    # Get a rpc client for the payment currency type
    client = CryptocurrencyClient(data["currency"])

    # Get the transaction data
    transaction_data = client.get_transaction(data["transaction"])
    data.update({
        "amount": transaction_data.amount,
        "fee": transaction_data.fee,
        "confirmations": transaction_data.confirmations,
        "category": transaction_data.category
    })

    # Find the payment associated with the receiving address
    payment = payments.get_payment(merchant_address=transaction_data.address)

    # If we have a payment for this address, store a reference to the payment
    if payment:
        data["payment_id"] = payment.id

    transaction_data, errors = TransactionSchema().load(data)
    transaction = Transaction(**transaction_data)

    if payment:
        payments.update_status(payment)

    return transaction