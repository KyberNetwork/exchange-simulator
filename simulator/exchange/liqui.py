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

    def _get_balance(self, api_key):
        balance = super().get_balance(api_key, ['available'])
        return balance['available']

    def get_balance_api(self, api_key, *args, **kargs):
        return {'funds': self._get_balance(api_key)}

    def trade_api(self, api_key, type, rate, pair, amount,
                  timestamp, *args, **kargs):
        result = self.trade(api_key, type, rate, pair, amount, timestamp)
        if result['remaining'] == 0:
            result['order_id'] = 0
        return {
            'received': result['received'],
            'remains': result['remaining'],
            'order_id': result['order_id'],
            'funds': self._get_balance(api_key)
        }

    def get_active_orders_api(self, api_key, pair, *args, **kargs):
        orders = self.get_all_orders(pair)
        result = {}
        for o in orders:
            if o.status in ['new', 'partially_filled']:
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
        if order.status in ['new', 'partially_filled']:
            stt = 0
        elif order.status == 'filled':
            stt = 1
        elif order.status == 'canceled':
            if order.executed_amount > 0:
                stt = 3
            else:
                stt = 2
        return {
            'pair': order.pair,
            'type': order.type,
            'start_amount': order.original_amount,
            'amount': order.remaining_amount,
            'rate': order.rate,
            'timestamp_created': 0,
            'status': stt
        }

    def cancel_order_api(self, api_key, order_id, *args, **kargs):
        self.cancel_order(api_key, order_id)
        return {
            'order_id': int(order_id),
            'funds': self._get_balance(api_key)
        }

    def withdraw_api(self, api_key, coinName, address, amount, *args, **kargs):
        tx = self.withdraw(api_key, coinName, address, amount)
        return {
            'tId': tx,
            'amountSent': amount,
            'funds': self._get_balance(api_key)
        }
