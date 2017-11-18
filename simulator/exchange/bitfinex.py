from .exchange import Exchange


class Bitfinex(Exchange):

    def __init__(self, *args):
        super().__init__(*args)

    def order_book_api(self, symbol, timestamp, *args, **kargs):
        base = symbol[:3]
        quote = symbol[-3:]
        pair = '_'.join([base, quote]).lower()
        order_book = self.get_order_book(pair, timestamp)
        asks = []
        for o in order_book['Asks']:
            asks.append({
                'price': str(o['Rate']),
                'amount': str(o['Quantity']),
                'timestamp': str(timestamp)
            })
        bids = []
        for o in order_book['Bids']:
            bids.append({
                'price': str(o['Rate']),
                'amount': str(o['Quantity']),
                'timestamp': str(timestamp)
            })
        return {'asks': asks, 'bids': bids}

    def balances_api(self, api_key, *args, **kargs):
        balance = self.balance.get(user=api_key)
        output = []
        for token in self.supported_tokens:
            result.append({
                'type': 'exchange',
                'currency': token.token,
                'amount': str(balance[token.token]),
                'available': str(balance[token.token])
            })
        return output

    def trade_api(self, api_key, symbol, amount, price, side,
                  timestamp, *args, **kargs):
        base = symbol[:3]
        quote = symbol[-3:]
        pair = '_'.join([base, quote]).lower()

        trade_result = self.trade(api_key, side, price, pair, amount, timestamp)

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
