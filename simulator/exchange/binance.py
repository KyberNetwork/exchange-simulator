from .exchange import Exchange
from .. import web3_interface, utils

logger = utils.get_logger()


class Binance(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

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
        available = self.balance.get(user=api_key, type='available')
        lock = self.balance.get(user=api_key, type='lock')
        balances = []
        for token in self.supported_tokens:
            balances.append({
                'asset': token.token.upper(),
                'free': str(available[token.token]),
                'locked': str(lock[token.token])
            })

        return {
            "makerCommission": 15,
            "takerCommission": 15,
            "buyerCommission": 0,
            "sellerCommission": 0,
            "canTrade": True,
            "canWithdraw": True,
            "canDeposit": True,
            "balances": balances
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
        orders = self.get_active_orders(pair)
        result = []
        for o in orders:
            output = self.__order_to_dict(o)
            output['status'] = 'NEW'
            result.append(output)
        return result

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
        tx = self.withdraw(api_key, asset, address, amount)
        return {
            'msg': 'success',
            'success': True,
            'id': str(tx)[2:]  # remove 0x in transaction id
        }

    def __order_to_dict(self, order):
        return {
            'symbol': self.__pair_to_symbol(order.pair),
            'orderId': order.id,
            'clientOrderId': 'myOrder1',
            'price': str(order.rate),
            'origQty': str(order.original_amount),
            'executedQty': str(order.executed_amount),
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
