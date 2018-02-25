from orderbook import OrderBook, Bid, Ask, orderbook_to_json


def test_to_json__empty():
    o = OrderBook(asks=[], bids=[])
    assert orderbook_to_json(o) == '{"Asks": [], "Bids": []}'


def test_to_json():
    asks = [Ask(quantity=1, rate=2)]
    bids = [Bid(quantity=3, rate=4)]
    o = OrderBook(asks=asks, bids=bids)

    j = orderbook_to_json(o)

    assert j == '{"Asks": [{"Quantity": 1, "Rate": 2}], "Bids": [{"Quantity": 3, "Rate": 4}]}'
