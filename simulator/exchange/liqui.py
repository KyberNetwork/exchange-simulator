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
        return {'funds': self.get_balance(user=api_key, type='available')}

    def trade_api(self, api_key, type, rate, pair, amount,
                  timestamp, *args, **kargs):
        result = self.trade(api_key, type, rate, pair, amount, timestamp)
        if result['remaining'] == 0:
            result['order_id'] = 0
        return {
            'received': result['received'],
            'remains': result['remaining'],
            'order_id': result['order_id'],
            'funds': self.get_balance(api_key, 'available')
        }

    def get_active_orders_api(self, api_key, pair, *args, **kargs):
        orders = self.get_active_orders(pair)
        result = {}
        for o in orders:
            if o.active():
                result[o.id] = {
                    'pair': o.pair,
                    'type': o.type,
                    'amount': o.remaining_amount,
                    'rate': o.rate,
                    'timestamp_created': 0,
                    'status': 0,
                }
        return result

    def get_order_api(self, order_id, *args, **kargs):
        order = self.get_order(order_id)
        return {
            'pair': order.pair,
            'type': order.type,
            'start_amount': order.original_amount,
            'amount': order.remaining_amount,
            'rate': order.rate,
            'timestamp_created': 0,
            'status': order.status()
        }

    def cancel_order_api(self, api_key, order_id, *args, **kargs):
        self.cancel_order(api_key, order_id)
        return {
            'order_id': int(order_id),
            'funds': self.get_balance(api_key, 'available')
        }

    def withdraw_api(self, api_key, coinName, address, amount, *args, **kargs):
        tx = self.withdraw(api_key, coinName, address, amount)
        return {
            'tId': tx,
            'amountSent': amount,
            'funds': self.get_balance(api_key, 'available')
        }
