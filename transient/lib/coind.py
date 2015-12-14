import dogecoinrpc
from dogecoinrpc.proxy import JSONRPCException
from transient import settings


class CoindClient(object):
    client = None

    def __init__(self, currency):
        self.currency = currency.upper()

        if self.currency == "DOGE":
            self.client = get_dogecoin_client()
        else:
            raise ValueError("Invalid currency or currency not yet supported")

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


def get_dogecoin_client():
    return dogecoinrpc.connect_to_remote(settings.DOGECOIN_RPC_USERNAME, settings.DOGECOIN_RPC_PASSWORD,
                                         host=settings.DOGECOIN_RPC_HOST, port=settings.DOGECOIN_RPC_PORT)
