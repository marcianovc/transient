from os import environ
import dogecoinrpc
from dogecoinrpc.proxy import JSONRPCException


class CoindClient():
    client = None

    def __init__(self, currency):
        self.currency = currency.upper()

        if self.currency == "DOGE":
            self.client = self.get_dogecoin_client()
        else:
            raise ValueError("Invalid currency or currency not yet supported")

    def get_dogecoin_client(self):
        return dogecoinrpc.connect_to_remote(
            environ.get("DOGECOIN_RPC_USERNAME"),
            environ.get("DOGECOIN_RPC_PASSWORD"),
            host=environ.get("DOGECOIN_RPC_HOST", "localhost"),
            port=environ.get("DOGECOIN_RPC_PORT", 8332)
        )

    def create_address(self):
        return self.client.getnewaddress()

    def get_transaction(self, txid):
        return self.client.gettransaction(txid)

    def is_valid_address(self, address):
        try:
            result = self.client.validateaddress(address)
            return result.isvalid
        except JSONRPCException, e:
            return False
