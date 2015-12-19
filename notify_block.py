#!/usr/bin/python
import sys
from transient.services.transactions import update_unconfirmed_transactions

if __name__ == '__main__':
    update_unconfirmed_transactions(currency=sys.argv[1])
