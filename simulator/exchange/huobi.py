from .exchange import Exchange
from .. import utils

logger = utils.get_logger()


class Huobi(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_info_api(self):
        return self.get_info()

    def get_depth_api(self, symbol, timestamp, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        order_book = self.get_order_book(pair, timestamp)
        asks = [[o['Rate'], o['Quantity']] for o in order_book['Asks']]
        bids = [[o['Rate'], o['Quantity']] for o in order_book['Bids']]
        return {
            'asks': asks,
            'bids': bids,
            'ts': 0,
            'version': 0
        }

    def get_balance_api(self, api_key, *args, **kargs):
        balance = self.get_balance(api_key)
        result = []
        for token in self.supported_tokens:
            result.extend([
                {
                    'currency': token.token,
                    'type': 'trade',
                    'balance': str(balance['available'][token.token])
                },
                {
                    'currnecy': token.token,
                    'type': 'frozen',
                    'balance': str(balance['lock'][token.token])
                }
            ])
        return {
            'id': 100009,
            'type': 'spot',
            'state': 'working',
            'list': result,
            'user-id': 1000
        }

    def trade_api(self, api_key, amount, price, symbol, type, timestamp,
                  *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        if 'sell' in type:
            side = 'sell'
        else:
            side = 'buy'
        result = self.trade(api_key, side, price, pair, amount, timestamp)
        return str(result['order_id'])

    def get_open_orders_api(self, symbol, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        orders = self.get_all_orders(pair)
        open_orders = filter(lambda o: o.status in [
                             'new', 'partially_filled'], orders)
        result = []
        for order in open_orders:
            result.append({
                "id": order.id,
                "symbol": symbol,
                "amount": str(order.original_amount),
                "price": str(order.rate),
                "state": order.status
            })
        return result

    def get_order_api(self, order_id, *args, **kargs):
        order = self.get_order(order_id)
        return {
            "id": order.id,
            "order-id": order.id,
            "symbol": self.__pair_to_symbol(order.pair),
            "price": str(order.rate),
            "filled-amount": str(order.executed_amount),
            "amount": str(order.remaining_amount),
            "state": order.status
        }

    def cancel_order_api(self, api_key, order_id, *args, **kargs):
        self.cancel_order(api_key, order_id)
        return str(order_id)

    def withdraw_api(self, api_key, address, amount, currency, *args, **kargs):
        result = self.withdraw(api_key, currency, address, amount)
        return result.id

    def history_api(self, types=None, *args, **kargs):
        if types == 'withdraw-virtual':
            withdraw = self.balance.get_history('withdraw').values()
            deposit = []
        elif types == 'deposit-virtual':
            withdraw = []
            deposit = self.balance.get_history('deposit').values()
        else:
            withdraw = self.balance.get_history('withdraw').values()
            deposit = self.balance.get_history('deposit').values()
        result = []
        for a in deposit:
            result.append({
                'transaction-id': a.id,
                'type': 'deposit-virtual',
                'direction': 'in',
                'currency': a.token,
                'amount': str(a.amount),
                'address': str(a.address),
                'tx-hash': str(a.tx),
                'state': 'safe'
            })
        for a in withdraw:
            result.append({
                'transaction-id': a.id * 100 + 1,
                'type': 'withdraw-virtual',
                'direction': 'out',
                'currency': a.token,
                'amount': str(a.amount),
                'address': str(a.address),
                'tx-hash': str(a.tx),
                'state': 'confirmed'
            })
        return result

    def __symbol_to_pair(self, symbol):
        base, quote = symbol[:-3], symbol[-3:]
        return '_'.join([base, quote])

    def __pair_to_symbol(self, pair):
        return ''.join(map(lambda x: x.lower(), pair.split('_')))
