from .exchange import Exchange
from .. import web3_interface, utils

logger = utils.get_logger()


class Binance(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def get_order_book_api(self, symbol, timestamp, *args, **kargs):
        base, quote = symbol[:-3], symbol[-3:]
        pair = '_'.join([base, quote]).lower()
        order_book = self.get_order_book(pair, timestamp)
        asks = [
            [str(o['Rate']), str(o['Quantity']), []] for o in order_book['Asks']
        ]
        bids = [
            [str(o['Rate']), str(o['Quantity']), []] for o in order_book['Bids']
        ]
        return {'lastUpdateId': timestamp, 'asks': asks, 'bids': bids}

    def get_account_api(self, api_key, *args, **kargs):
        balance = self.balance.get(user=api_key)

        balances = []
        for token in self.supported_tokens:
            balances.append({
                'asset': token.token.upper(),
                'free': str(balance[token.token]),
                'locked': "0.0"
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
        base = symbol[:-3]
        quote = symbol[-3:]
        pair = '_'.join([base, quote]).lower()

        result = self.trade(api_key, side, price, pair, quantity, timestamp)
        return {
            'symbol': symbol,
            'orderId': result['order_id'],
            'clientOrderId': 'myOrder1',  # Will be newClientOrderId
            'transactTime': utils.get_current_timestamp()
        }

    def get_order_api(self, orderId, *args, **kargs):
        try:
            order = self.get_order(orderId)
            return {
                'symbol': order.pair.upper(),
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
                'time': utils.get_current_timestamp()
            }
        except Exception:
            raise ValueError('Order not found')

    def withdraw_api(self, api_key, asset, amount, address, *args, **kargs):
        tx = self.withdraw(api_key, asset, address, amount)
        return {
            'msg': 'success',
            'success': True,
            'id': str(tx)[2:]  # remove 0x in transaction id
        }
