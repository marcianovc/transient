import dogecoinrpc
from os import environ


class CryptocurrencyClient():
    client = None

    def __init__(self):
        self.client = self.get_client()

    def get_new_address(self):
        return self.client.getnewaddress()

    def get_transaction(self, txid):
        result = self.client.getrawtransaction(txid)
        return result

    def is_valid_address(self, address):
        try:
            result = self.client.validateaddress(address)
            return result.isvalid
        except JSONRPCException, e:
            return False


class DogecoinClient(CryptocurrencyClient):

    def get_client(self):
        if not self.client:
            self.client = dogecoinrpc.connect_to_remote(
                environ.get("DOGECOIN_RPC_USERNAME"),
                environ.get("DOGECOIN_RPC_PASSWORD"),
                host=environ.get("DOGECOIN_RPC_HOST", "localhost"),
                port=environ.get("DOGECOIN_RPC_PORT", 8332)
            )
        return self.client
