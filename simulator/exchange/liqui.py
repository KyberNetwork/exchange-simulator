from .exchange import Exchange
from .. import utils

logger = utils.get_logger()


class Liqui(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_depth_api(self, pairs, timestamp):
        depth = {}
        pairs = pairs.split('-')
        for pair in pairs:
            order_book = self.get_order_book(pair, timestamp)
            depth[pair] = {
                "asks": [
                    [o['Rate'], o['Quantity']] for o in order_book['Asks']
                ],
                "bids": [
                    [o['Rate'], o['Quantity']] for o in order_book['Bids']
                ],
            }
        return depth

    def get_balance_api(self, api_key, *args, **kargs):
        return {'funds': self.get_balance(api_key)}

    def trade_api(self, api_key, type, rate, pair, amount,
                  timestamp, *args, **kargs):
        result = self.trade(api_key, type, rate, pair, amount, timestamp)
        return result

    def withdraw_api(self, api_key, coinName, address, amount, *args, **kargs):
        tx = self.withdraw(api_key, coinName, address, amount)
        return {
            'tId': tx,
            'amountSent': amount,
            'funds': self.get_balance(api_key)
        }
