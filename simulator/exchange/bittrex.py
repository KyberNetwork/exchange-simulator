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
        blc = self.get_balance(api_key=apikey)
        result = []
        for token in self.supported_tokens:
            asset = token.token
            result.append({
                'Currency': asset.upper(),
                'Balance': blc['available'][asset] + blc['lock'][asset],
                'Available': blc['available'][asset],
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
        tx = self.withdraw(apikey, currency, address, quantity)
        return {'uuid': tx}
