import json
from collections import namedtuple

Ask = namedtuple('Ask', ['quantity', 'rate'])
Bid = namedtuple('Bid', ['quantity', 'rate'])

OrderBook = namedtuple('OrderBook', ['asks', 'bids'])


def orderbook_to_json(orderbook):
    return json.dumps({'Asks': [{'Quantity': ask.quantity, 'Rate': ask.rate} for ask in orderbook.asks],
                       'Bids': [{'Quantity': bid.quantity, 'Rate': bid.rate} for bid in orderbook.bids]})
