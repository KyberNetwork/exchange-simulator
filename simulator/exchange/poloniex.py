from .exchange import Exchange
from .. import utils
from collections import defaultdict

logger = utils.get_logger()


class Poloniex(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def order_book_api(self, currencyPair, timestamp, *args, **kargs):
        pair = self.__currency_pair_to_pair(currencyPair)
        order_book = self.get_order_book(pair, timestamp)
        return order_book

    def __currency_pair_to_pair(self, currency_pair):
        quote, base = currency_pair.split('_')
        return '_'.join([base, quote]).lower()

    def __pair_to_currency_pair(self, pair):
        base, quote = pair.split('_')
        return '_'.join([quote, base]).upper()

    def get_balance_api(self, api_key, *args, **kargs):
        blc = self.get_balance(api_key)
        result = {}
        for token in self.supported_tokens:
            tk = token.token
            result[tk.upper()] = str(blc['available'][tk] + blc['lock'][tk])
        return result

    def trade_api(self, api_key, currencyPair, rate, amount, type,
                  timestamp, *args, **kargs):
        pair = self.__currency_pair_to_pair(currencyPair)
        result = self.trade(api_key, type, rate, pair, amount, timestamp)
        return {
            'orderNumber': result['order_id'],
            'resultingTrades': [{
                'amount': str(amount),
                'date': '',
                'rate': str(rate),
                'total': str(result['received']),
                'tradeId': '',
                'type': type
            }]}

    def get_open_orders_api(self, api_key, currencyPair, *args, **kargs):
        orders = self.get_all_orders()
        open_orders = filter(lambda o: o.status in [
                             'new', 'partially_filled'], orders)
        result = defaultdict(list)
        for o in open_orders:
            cp = self.__pair_to_currency_pair(o.pair)
            result[cp].append(self.__format_order(o))

        if currencyPair == 'all':
            return result
        else:
            return result[currencyPair]

    def cancel_order_api(self, api_key, orderNumber, *args, **kargs):
        self.cancel_order(api_key, orderNumber)
        return {'success': 1}

    def get_history_api(self, *args, **kargs):
        withdraw = self.balance.get_history('withdraw').values()
        deposit = self.balance.get_history('deposit').values()

        return {
            'deposits': list(map(self.__format_history, deposit)),
            'withdrawals': list(map(self.__format_history, withdraw))
        }

    def withdraw_api(self, api_key, currency, amount, address, *args, **kargs):
        self.withdraw(api_key, currency, address, amount)
        return {
            'response': 'Withdrew {} {}.'.format(amount, currency)
        }

    def __format_order(self, o):
        return {
            'orderNumber': str(o.id),
            'type': o.type,
            'rate': o.rate,
            'amount': str(o.remaining_amount),
            'total': str(o.rate * o.remaining_amount)
        }

    def __format_history(self, h):
        return {
            'currency': h.token.upper(),
            'address': h.address,
            'amount': h.amount,
            'txid': h.tx,
            'timestamp': str(h.timestamp),
            'status': 'COMPLETE'
        }
