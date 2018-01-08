from .exchange import Exchange
from .. import utils

logger = utils.get_logger()


class Binance(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_info_api(self):
        result = {
            'timezone': 'UTC',
            'serverTime': utils.get_timestamp()
        }
        result.update(self.get_info())
        return result

    def get_order_book_api(self, symbol, timestamp, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        order_book = self.get_order_book(pair, timestamp)
        asks = [
            [str(o['Rate']), str(o['Quantity']), []] for o in order_book['Asks']
        ]
        bids = [
            [str(o['Rate']), str(o['Quantity']), []] for o in order_book['Bids']
        ]
        return {'lastUpdateId': timestamp, 'asks': asks, 'bids': bids}

    def get_account_api(self, api_key, *args, **kargs):
        balance = self.get_balance(api_key)
        result = []
        for token in self.supported_tokens:
            result.append({
                'asset': token.token.upper(),
                'free': str(balance['available'][token.token]),
                'locked': str(balance['lock'][token.token])
            })

        return {
            "makerCommission": 15,
            "takerCommission": 15,
            "buyerCommission": 0,
            "sellerCommission": 0,
            "canTrade": True,
            "canWithdraw": True,
            "canDeposit": True,
            "balances": result
        }

    def trade_api(self, api_key, symbol, quantity, price, side,
                  timestamp, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        result = self.trade(api_key, side, price, pair, quantity, timestamp)
        return {
            'symbol': symbol,
            'orderId': result['order_id'],
            'clientOrderId': 'myOrder1',  # Will be newClientOrderId
            'transactTime': 0
        }

    def get_all_orders_api(self, api_key, symbol, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        orders = self.get_all_orders(pair)
        return list(map(self.__order_to_dict, orders))

    def get_open_orders_api(self, api_key, symbol, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        orders = self.get_all_orders(pair)
        open_orders = filter(lambda o: o.status in [
                             'new', 'partially_filled'], orders)
        return list(map(self.__order_to_dict, open_orders))

    def get_order_api(self, orderId, *args, **kargs):
        order = self.get_order(orderId)
        return self.__order_to_dict(order)

    def cancel_order_api(self, api_key, symbol, orderId, *args, **kargs):
        self.cancel_order(api_key, orderId)
        return {
            'symbol': symbol,
            'orderId': int(orderId),
            'origClientOrderId': 'origClientOrderId',
            'clientOrderId': 'clientOrderId'
        }

    def withdraw_api(self, api_key, asset, amount, address, *args, **kargs):
        result = self.withdraw(api_key, asset, address, amount)
        return {
            'msg': 'success',
            'success': True,
            'id': str(result.uuid)
        }

    def withdraw_history_api(self, *args, **kargs):
        def format(a):
            return {
                'id': str(a.uuid),
                'amount': a.amount,
                'address': a.address,
                'asset': a.token.upper(),
                'txId': str(a.tx),
                'applyTime': a.timestamp,
                'status': 6  # completed
            }
        activities = self.balance.get_history('withdraw').values()
        return {
            'withdrawList': [format(a) for a in activities],
            'success': True
        }

    def deposit_history_api(self, *args, **kargs):
        def format(a):
            return {
                'amount': a.amount,
                'address': a.address,
                'asset': a.token.upper(),
                'txId': str(a.tx),
                'insertTime': a.timestamp,
                'status': 1  # completed
            }
        activities = self.balance.get_history('deposit').values()
        return {
            'depositList': [format(a) for a in activities],
            'success': True
        }

    def __order_to_dict(self, order):
        return {
            'symbol': self.__pair_to_symbol(order.pair),
            'orderId': order.id,
            'clientOrderId': 'myOrder1',
            'price': str(order.rate),
            'origQty': str(order.original_amount),
            'executedQty': str(order.executed_amount),
            'status': order.status.upper(),
            'timeInForce': 'GTC',
            'type': 'LIMIT',
            'side': order.type,
            'stopPrice': '0.0',
            'icebergQty': '0.0',
            'time': 0
        }

    def __symbol_to_pair(self, symbol):
        base, quote = symbol[:-3], symbol[-3:]
        return '_'.join([base, quote]).lower()

    def __pair_to_symbol(self, pair):
        return ''.join(map(lambda x: x.upper(), pair.split('_')))
