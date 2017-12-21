from .exchange import Exchange
from .. import utils

logger = utils.get_logger()


class Bittrex(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_order_book_api(self, market, type, timestamp, *args, **kargs):
        pair = self.__market_to_pair(market)
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
        blc = self.get_balance(api_key=apikey, blc_types=['available'])
        result = []
        for token in self.supported_tokens:
            asset = token.token
            result.append({
                'Currency': asset.upper(),
                'Balance': blc['available'][asset],
                'Available': blc['available'][asset],
                'Pending': 0.0,
                'CryptoAddress': hex(token.address),
                'Requested': False,
                'Uuid': None
            })
        return result

    def trade_api(self, apikey, market, quantity, rate,
                  type, timestamp, *args, **kargs):
        pair = self.__market_to_pair(market)
        result = self.trade(apikey, type, rate,
                            pair, quantity, timestamp)
        return {'uuid': str(result['order_id'])}

    def get_open_orders_api(self, market, *args, **kargs):
        if market:
            pair = self.__market_to_pair(market)
        else:
            pair = None
        orders = self.get_all_orders(pair)
        open_orders = filter(lambda o: o.status in [
                             'new', 'partially_filled'], orders)
        return list(map(self.__order_to_dict, open_orders))

    def get_order_api(self, uuid, *args, **kargs):
        order = self.get_order(uuid)
        return self.__order_to_dict(order)

    def cancel_order_api(self, apikey, uuid, *args, **kargs):
        self.cancel_order(apikey, uuid)

    def withdraw_api(self, apikey, currency, quantity, address, *args, **kargs):
        result = self.withdraw(apikey, currency, address, quantity)
        return {'uuid': result.uuid}

    def history_api(self, apikey, currency, act_type, *args, **kargs):
        all_acts = self.balance.get_history(act_type).values()
        if currency:
            acts = filter(lambda a: a.token == currency.lower(), all_acts)
        else:
            acts = all_acts
        return [self.__format_activity(a, act_type) for a in acts]

    def __format_activity(self, a, act_type):
        tx = a.tx
        if act_type == 'deposit':
            return {
                'Id': 0,
                'Amount': a.amount,
                'Currency': a.token.upper(),
                'Confirmations': 42,
                'LastUpdated': utils.bittrex_fmt_time(a.timestamp),
                'TxId': '0xdeposit_tx',
                'CryptoAddress': hex(utils.get_token(a.token).address)
            }
        else:
            return {
                'PaymentUuid': a.uuid,
                'Currency': a.token.upper(),
                'Amount': a.amount,
                'Address': a.address,
                'Opened': utils.bittrex_fmt_time(a.timestamp),
                'Authorized': True,
                'PendingPayment': False,
                'TxCost': 0,
                'TxId': a.tx,
                'Canceled': False,
                'InvalidAddress': False
            }

    def __market_to_pair(self, market):
        try:
            quote, base = market.split('-')
        except:
            raise ValueError('Invalid pair {}.'.format(market))
        return '_'.join([base, quote]).lower()

    def __pair_to_market(self, pair):
        base, quote = pair.split('_')
        return '-'.join([quote, base]).upper()

    def __order_to_dict(self, o):
        is_open = o.status in ['new', 'partially_filled']
        return {
            'Uuid': str(o.id),
            'OrderUuid': str(o.id),
            'Exchange': self.__pair_to_market(o.pair),
            'OrderType': 'LIMIT_{}'.format(o.type.upper()),
            'Quantity': o.original_amount,
            'QuantityRemaining': o.remaining_amount,
            'Limit': 0,
            'CommissionPaid': 0,
            'Price': o.rate,
            'PricePerUnit': None,
            'Opened': '2014-07-09T03:55:48.77',
            'Closed': None,
            'IsOpen': is_open,
            'CancelInitiated': False,
            'ImmediateOrCancel': False,
            'IsConditional': False,
            'Condition': None,
            'ConditionTarget': None
        }
