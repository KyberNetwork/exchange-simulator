from .exchange import Exchange
from .. import web3_interface, utils

logger = utils.get_logger()


class Bittrex(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_order_book_api(self, market, type, timestamp):
        quote, base = market.split('-')
        pair = '_'.join([base, quote]).lower()
        order_book = self.get_order_book(pair, timestamp)

        if type == 'sell':
            result = order_book['Asks']
        elif type == 'buy':
            result = order_book['Bids']
        elif type == 'both':
            result = {
                'sell': order_book['Asks'],
                'buy': order_book['Bids']
            }
        return result

    def get_balance_api(self, apikey, *args, **kargs):
        balance = self.balance.get(user=apikey)
        result = []
        for token in self.supported_tokens:
            result.append({
                'Currency': token.token.upper(),
                'Balance': balance[token.token],
                'Available': balance[token.token],
                'Pending': 0.0,
                'CryptoAddress': hex(token.address),
                'Requested': False,
                'Uuid': None
            })
        return result

    def trade_api(self, apikey, market, quantity, rate,
                  type, timestamp, *args, **kargs):
        quote, base = market.split('-')
        pair = '_'.join([base, quote]).lower()
        result = self.trade(apikey, type, rate,
                            pair, quantity, timestamp)
        return {'uuid': result['order_id']}

    def withdraw_api(self, apikey, currency, quantity, address, *args, **kargs):
        tx = self.withdraw(apikey, currency, quantity, address)
        return {'uuid': tx}
