from .exchange import Exchange
from . import web3_interface, utils

logger = utils.get_logger()


class Binance(Exchange):
    def __init__(self, *args):
        super().__init__(*args)

    def get_order_book_api(self, symbol, timestamp, *args, **kargs):
        base = symbol[:3]
        quote = symbol[-3:]
        pair = '_'.join([base, quote]).lower()
        logger.info('Pair: {}'.format(pair))

        order_book = super().get_order_book(pair, timestamp)
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

    def trades(self, api_key, symbol, quantity, price, side,
               timestamp, *args, **kargs):
        base = symbol[:3]
        quote = symbol[-3:]
        pair = '_'.join([base, quote]).lower()

        result = super().trade_api(api_key, side, price,
                                   pair, quantity, timestamp)
        return {
            'symbol': symbol,
            'orderId': result['order_id'],
            'clientOrderId': 'myOrder1',  # Will be newClientOrderId
            'transactTime': utils.get_current_timestamp()
        }

    def withdraw_api(self, api_key, asset, amount, address, *args, **kargs):
        asset = asset.lower()
        amount = float(amount)
        self.balance.withdraw(user=api_key, token=asset, amount=amount)
        token = utils.get_token(asset)
        tx = web3_interface.withdraw(self.deposit_address,
                                     token.address,
                                     int(quantity * 10**token.decimals),
                                     address)
        return {
            'msg': 'success',
            'success': True
        }