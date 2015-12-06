#!/usr/bin/python
import sys
from app.payments import create_transaction

if __name__ == '__main__':
    create_transaction({
        'transaction_id': sys.argv[2],
        'currency': sys.argv[1]
    })
