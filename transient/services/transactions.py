from sqlalchemy.orm import aliased
from transient.models.payment import Payment
from transient.models.transaction import Transaction, TransactionSchema
from transient.services import payments
from transient.lib.coind import CoindClient


def get_transaction(id=None, **filters):
    if id:
        return Transaction.query.get(id)
    else:
        return Transaction.query.filter_by(**filters).first()


def get_unconfirmed(currency):
    payment = aliased(Payment)
    return Transaction.query.join(payment, Transaction.payment)\
        .filter(Transaction.currency==currency)\
        .filter(Transaction.confirmations<payment.confirmations_required)


def create_transaction(**data):
    if not data["transaction"]:
        raise ValueError("Transaction ID is required")

    # If we already had the transaction recorded, we can just update the confirmations
    transaction = get_transaction(transaction_id=data["transaction"])

    # Get a rpc client for the payment currency type
    client = CoindClient(data["currency"])

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

    # Either update the confirmations on the existing transaction, or create a new transaction
    if transaction:
        transaction.confirmations = transaction_data.confirmations
    else:
        if payment:
            data["payment_id"] = payment.id
        transaction_data, errors = TransactionSchema().load(data)
        transaction = Transaction(**transaction_data)

    if payment:
        payments.update_status(payment)

    return transaction


def update_unconfirmed_transactions(currency):
    transactions = get_unconfirmed(currency)
    client = CoindClient(currency)
    updated_transactions = []

    # Update the confirmations count of unconfirmed transactions
    for transaction in transactions:
        info = client.get_transaction(transaction.transaction_id)
        if info.confirmations != transaction.confirmations:
            transaction.confirmations = info.confirmations
            updated_transactions.append(transaction)

    # Update the status of any payments that had changes in their transactions
    updated_payments = list(set([t.payment_id for t in updated_transactions]))
    for payment_id in updated_payments:
        payments.update_status(payment_id)

    return updated_transactions
