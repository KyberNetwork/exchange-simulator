from .exchange import Exchange
from .. import utils

logger = utils.get_logger()


class Bitfinex(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def order_book_api(self, symbol, timestamp, *args, **kargs):
        def convert(o):
            return {
                'price': str(o['Rate']),
                'amount': str(o['Quantity']),
                'timestamp': str(timestamp)
            }
        pair = self.__symbol_to_pair(symbol)
        order_book = self.get_order_book(pair, timestamp)
        return {
            'asks': list(map(convert, order_book['Asks'])),
            'bids': list(map(convert, order_book['Bids']))
        }

    def balances_api(self, api_key, *args, **kargs):
        blc = self.get_balance(api_key=api_key)
        output = []
        for token in self.supported_tokens:
            output.append({
                'type': 'exchange',
                'currency': token.token,
                'amount': str(blc['available'][token.token]),
                'available': str(blc['available'][token.token])
            })
            output.append({
                'type': 'trading',
                'currency': token.token,
                'amount': str(blc['lock'][token.token]),
                'available': str(0)
            })
        return output

    def trade_api(self, api_key, symbol, amount, price, side,
                  timestamp, *args, **kargs):
        pair = self.__symbol_to_pair(symbol)
        result = self.trade(api_key, side, price, pair, amount, timestamp)
        return {
            'symbol': symbol.lower(),
            'exchange': self.name,
            'price': str(price),
            'avg_execution_price': str(price),
            'side': side,
            'type': 'exchange_limit',
            'timestamp': str(timestamp),
            'is_live': True,
            'is_cancelled': False,
            'is_hidden': False,
            'was_forced': False,
            'original_amount': str(amount),
            'remaining_amount': str(result['remaining']),
            'executed_amount': str(result['received']),
            'order_id': result['order_id']
        }

    def active_orders_api(self, *args, **kargs):
        orders = self.get_all_orders()
        open_orders = filter(lambda o: o.status in [
            'new', 'partially_filled'
        ], orders)
        return list(map(self.__format_order, open_orders))

    def order_status_api(self, order_id, *args, **kargs):
        order = self.get_order(order_id)
        return self.__format_order(order)

    def cancel_order_api(self, api_key, order_id, *args, **kargs):
        self.cancel_order(api_key, order_id)
        order = self.orders.get(order_id)
        return self.__format_order(order)

    def withdraw_api(self, api_key, withdraw_type, amount, address,
                     *args, **kargs):
        # TODO convert withdraw_type to token
        # e.g: ethereum -> eth
        tx = self.withdraw(api_key, withdraw_type[:3], address, amount)
        return [{
            'status': 'success',
            'message': 'Your withdrawal request has been successfully submitted.',
            'withdrawal_id': tx
        }]

    def history_api(self, currency, *args, **kargs):
        withdraw = self.balance.get_history('withdraw').values()
        deposit = self.balance.get_history('deposit').values()

        result = []
        for h in withdraw:
            if h.token == currency:
                format_h = self.__format_history(h)
                format_h['type'] = 'WITHDRAWAL'
                result.append(format_h)

        for h in deposit:
            if h.token == currency:
                format_h = self.__format_history(h)
                format_h['type'] = 'DEPOSIT'
                result.append(format_h)

        return result

    def __symbol_to_pair(self, symbol):
        base, quote = symbol[:-3], symbol[-3:]
        return '_'.join([base, quote]).lower()

    def __pair_to_symbol(self, pair):
        base, quote = pair.split('_')
        return ''.join([base, quote]).lower()

    def __format_order(self, o):
        return {
            'id': int(o.id),
            'symbol': self.__pair_to_symbol(o.pair),
            'exchange': self.name,
            'price': o.rate,
            'avg_execution_price': '0.0',
            'side': o.type,
            'type': 'exchange limit',
            'timestamp': '1',
            'is_live': True,
            'is_cancelled': False,
            'is_hidden': False,
            'was_forced': False,
            'original_amount': str(o.original_amount),
            'remaining_amount': str(o.remaining_amount),
            'executed_amount': str(o.executed_amount)
        }

    def __format_history(self, h):
        return {
            'id': h.tx,
            'txid': h.tx,
            'currency': h.token,
            'method': h.token,
            'amount': str(h.amount),
            'description': '',
            'address': h.address,
            'status': 'COMPLETED',
            'timestamp': str(h.timestamp),
            'timestamp_created': str(h.timestamp),
            'fee': 0.0
        }
