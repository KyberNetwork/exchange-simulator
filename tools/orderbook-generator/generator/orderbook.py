import json
import logging
from collections import namedtuple
import random
import operator

Ask = namedtuple('Ask', ['quantity', 'rate'])
Bid = namedtuple('Bid', ['quantity', 'rate'])

OrderBook = namedtuple('OrderBook', ['asks', 'bids'])

OrderBookGenerationParams = namedtuple("OrderBookGenerationParams",
                                       [
                                           'exchanges',
                                           'tokens',
                                           'base_token',
                                           'timestamp_start',
                                           'timestamp_stop',
                                           'timestamp_step',
                                           'min_quantity',
                                           'max_quantity',
                                           'min_rate',
                                           'max_rate',
                                           'number_of_asks',
                                           'number_of_bids',
                                           'middle_rate',
                                           'rate_gap'
                                       ])
log = logging.getLogger(__name__)


# 127.0.0.1:6379> get binance_trx_eth_1518228220000
# "{\"Asks\": [{\"Quantity\": 1837, \"Rate\": 6.129e-05}, {\"Quantity\": 90674, \"Rate\": 6.13e-05}, {\"Quantity\": 1132, \"Rate\": 6.132e-05}, {\"Quantity\": 943, \"Rate\": 6.135e-05}, {\"Quantity\": 6304, \"Rate\": 6.14e-05}, {\"Quantity\": 1275, \"Rate\": 6.145e-05}, {\"Quantity\": 5332, \"Rate\": 6.149e-05}, {\"Quantity\": 2400, \"Rate\": 6.15e-05}, {\"Quantity\": 64719, \"Rate\": 6.153e-05}, {\"Quantity\": 79810, \"Rate\": 6.154e-05}, {\"Quantity\": 19359, \"Rate\": 6.155e-05}, {\"Quantity\": 1033, \"Rate\": 6.156e-05}, {\"Quantity\": 3882, \"Rate\": 6.157e-05}, {\"Quantity\": 25871, \"Rate\": 6.159e-05}, {\"Quantity\": 4184839, \"Rate\": 6.16e-05}, {\"Quantity\": 47329, \"Rate\": 6.164e-05}, {\"Quantity\": 70905, \"Rate\": 6.17e-05}, {\"Quantity\": 449, \"Rate\": 6.172e-05}, {\"Quantity\": 162, \"Rate\": 6.173e-05}, {\"Quantity\": 10124, \"Rate\": 6.175e-05}, {\"Quantity\": 286, \"Rate\": 6.177e-05}, {\"Quantity\": 43285, \"Rate\": 6.18e-05}, {\"Quantity\": 369, \"Rate\": 6.182e-05}, {\"Quantity\": 6874, \"Rate\": 6.185e-05}, {\"Quantity\": 4082, \"Rate\": 6.187e-05}, {\"Quantity\": 14829, \"Rate\": 6.19e-05}, {\"Quantity\": 4175, \"Rate\": 6.193e-05}, {\"Quantity\": 23334, \"Rate\": 6.194e-05}, {\"Quantity\": 634, \"Rate\": 6.196e-05}, {\"Quantity\": 33325, \"Rate\": 6.198e-05}, {\"Quantity\": 48302, \"Rate\": 6.199e-05}, {\"Quantity\": 97796, \"Rate\": 6.2e-05}, {\"Quantity\": 44666, \"Rate\": 6.205e-05}, {\"Quantity\": 22958, \"Rate\": 6.206e-05}, {\"Quantity\": 3650, \"Rate\": 6.207e-05}, {\"Quantity\": 3760, \"Rate\": 6.209e-05}, {\"Quantity\": 41596, \"Rate\": 6.21e-05}, {\"Quantity\": 2365, \"Rate\": 6.212e-05}, {\"Quantity\": 27688, \"Rate\": 6.213e-05}, {\"Quantity\": 62071, \"Rate\": 6.214e-05}, {\"Quantity\": 23374, \"Rate\": 6.215e-05}, {\"Quantity\": 8260, \"Rate\": 6.219e-05}, {\"Quantity\": 18520, \"Rate\": 6.22e-05}, {\"Quantity\": 50887, \"Rate\": 6.225e-05}, {\"Quantity\": 600, \"Rate\": 6.227e-05}, {\"Quantity\": 211461, \"Rate\": 6.23e-05}, {\"Quantity\": 8950, \"Rate\": 6.231e-05}, {\"Quantity\": 2097, \"Rate\": 6.233e-05}, {\"Quantity\": 4071, \"Rate\": 6.235e-05}, {\"Quantity\": 403, \"Rate\": 6.24e-05}], \"Bids\": [{\"Quantity\": 46509, \"Rate\": 6.121e-05}, {\"Quantity\": 2800, \"Rate\": 6.114e-05}, {\"Quantity\": 70000, \"Rate\": 6.113e-05}, {\"Quantity\": 3000, \"Rate\": 6.112e-05}, {\"Quantity\": 334, \"Rate\": 6.108e-05}, {\"Quantity\": 40000, \"Rate\": 6.107e-05}, {\"Quantity\": 57673, \"Rate\": 6.105e-05}, {\"Quantity\": 2002, \"Rate\": 6.104e-05}, {\"Quantity\": 121980, \"Rate\": 6.101e-05}, {\"Quantity\": 167327, \"Rate\": 6.1e-05}, {\"Quantity\": 281, \"Rate\": 6.099e-05}, {\"Quantity\": 256, \"Rate\": 6.098e-05}, {\"Quantity\": 174670, \"Rate\": 6.09e-05}, {\"Quantity\": 5572, \"Rate\": 6.084e-05}, {\"Quantity\": 6773, \"Rate\": 6.083e-05}, {\"Quantity\": 17125, \"Rate\": 6.08e-05}, {\"Quantity\": 4771, \"Rate\": 6.078e-05}, {\"Quantity\": 197, \"Rate\": 6.077e-05}, {\"Quantity\": 65556, \"Rate\": 6.076e-05}, {\"Quantity\": 65865, \"Rate\": 6.073e-05}, {\"Quantity\": 53008, \"Rate\": 6.07e-05}, {\"Quantity\": 1648, \"Rate\": 6.068e-05}, {\"Quantity\": 45356, \"Rate\": 6.065e-05}, {\"Quantity\": 518, \"Rate\": 6.064e-05}, {\"Quantity\": 62540, \"Rate\": 6.06e-05}, {\"Quantity\": 6000, \"Rate\": 6.059e-05}, {\"Quantity\": 3902, \"Rate\": 6.055e-05}, {\"Quantity\": 5672, \"Rate\": 6.053e-05}, {\"Quantity\": 415, \"Rate\": 6.051e-05}, {\"Quantity\": 71118, \"Rate\": 6.05e-05}, {\"Quantity\": 10501, \"Rate\": 6.047e-05}, {\"Quantity\": 2407, \"Rate\": 6.045e-05}, {\"Quantity\": 779, \"Rate\": 6.044e-05}, {\"Quantity\": 320, \"Rate\": 6.043e-05}, {\"Quantity\": 613, \"Rate\": 6.041e-05}, {\"Quantity\": 11789, \"Rate\": 6.04e-05}, {\"Quantity\": 319, \"Rate\": 6.035e-05}, {\"Quantity\": 2800, \"Rate\": 6.033e-05}, {\"Quantity\": 1895, \"Rate\": 6.032e-05}, {\"Quantity\": 1375, \"Rate\": 6.03e-05}, {\"Quantity\": 56497, \"Rate\": 6.027e-05}, {\"Quantity\": 3741, \"Rate\": 6.025e-05}, {\"Quantity\": 365, \"Rate\": 6.024e-05}, {\"Quantity\": 1333, \"Rate\": 6.022e-05}, {\"Quantity\": 61940, \"Rate\": 6.021e-05}, {\"Quantity\": 5112, \"Rate\": 6.02e-05}, {\"Quantity\": 648, \"Rate\": 6.019e-05}, {\"Quantity\": 140091, \"Rate\": 6.015e-05}, {\"Quantity\": 336, \"Rate\": 6.014e-05}, {\"Quantity\": 2800, \"Rate\": 6.011e-05}]}"

def orderbook_to_json(orderbook):
    return json.dumps({'Asks': [{'Quantity': ask.quantity, 'Rate': ask.rate} for ask in orderbook.asks],
                       'Bids': [{'Quantity': bid.quantity, 'Rate': bid.rate} for bid in orderbook.bids]})


def _prepare_book_name(exchange, token, base_token, timestamp):
    return f"{exchange}_{token.lower()}_{base_token.lower()}_{timestamp}"


def prepare_timestamp_range(timestamp_start, timestamp_stop, timestamp_step):
    return range(timestamp_start, timestamp_stop, timestamp_step)


def prepare_random_order_book_from_params(params):
    return prepare_single_randomized_order_book(min_quantity=params.min_quantity,
                                                max_quantity=params.max_quantity,
                                                min_rate=params.min_rate,
                                                max_rate=params.max_rate,
                                                middle_rate=params.middle_rate,
                                                rate_gap=params.rate_gap,
                                                number_of_asks=params.number_of_asks,
                                                number_of_bids=params.number_of_bids)


def prepare_single_randomized_order_book(min_quantity, max_quantity, min_rate, max_rate, middle_rate, rate_gap,
                                         number_of_asks, number_of_bids):
    """Prepares a single randomized order book.

    - Ask prices increase
    - Bid prices decrease
    - Ask and Bid do not overlap
    """
    min_ask_price = middle_rate + rate_gap
    max_ask_price = max_rate
    asks = [
        Ask(quantity=random.uniform(min_quantity, max_quantity), rate=random.uniform(min_ask_price, max_ask_price))
        for _ in range(number_of_asks)
    ]
    asks.sort(key=operator.attrgetter('rate'))

    min_bid_price = min_rate
    max_bid_price = middle_rate - rate_gap
    bids = [
        Bid(quantity=random.uniform(min_quantity, max_quantity), rate=random.uniform(min_bid_price, max_bid_price))
        for _ in range(number_of_bids)
    ]
    bids.sort(key=operator.attrgetter('rate'), reverse=True)

    return OrderBook(asks=asks, bids=bids)


class OrderBookGenerator:
    async def prepare_books(self):
        raise NotImplementedError()


class DistinctRandomOrderBooksGenerator(OrderBookGenerator):
    def __init__(self, params):
        self.params = params

    async def prepare_books(self):
        books = {}
        for exchange in self.params.exchanges:
            for token in self.params.tokens:
                for timestamp in prepare_timestamp_range(self.params.timestamp_start,
                                                         self.params.timestamp_stop,
                                                         self.params.timestamp_step):
                    books[_prepare_book_name(exchange, token, self.params.base_token, timestamp)] = \
                        prepare_random_order_book_from_params(self.params)

        return books


class BlockRandomOrderBookGenerator(OrderBookGenerator):
    def __init__(self, params, timestamp_step=30_000):
        self.params = params
        self.timestamp_step = timestamp_step

    async def prepare_books(self):
        books = {}
        for exchange in self.params.exchanges:
            for token in self.params.tokens:
                timestamp_range = prepare_timestamp_range(self.params.timestamp_start,
                                                          self.params.timestamp_stop,
                                                          self.params.timestamp_step)
                last_randomized_timestamp = timestamp_range[0]
                order_book = prepare_random_order_book_from_params(self.params)
                for timestamp in timestamp_range:
                    if timestamp - last_randomized_timestamp >= self.timestamp_step:
                        order_book = prepare_random_order_book_from_params(self.params)
                        last_randomized_timestamp = timestamp
                    books[_prepare_book_name(exchange, token, self.params.base_token, timestamp)] = order_book

        return books


class StaticOrderBookGenerator(OrderBookGenerator):
    def __init__(self, params):
        self.params = params

    async def prepare_books(self):
        books = {}
        order_book = prepare_random_order_book_from_params(self.params)
        for exchange in self.params.exchanges:
            for token in self.params.tokens:
                timestamp_range = prepare_timestamp_range(self.params.timestamp_start,
                                                          self.params.timestamp_stop,
                                                          self.params.timestamp_step)
                for timestamp in timestamp_range:
                    books[_prepare_book_name(exchange, token, self.params.base_token, timestamp)] = order_book

        return books
