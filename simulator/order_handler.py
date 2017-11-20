import requests
import json

from . import utils

logger = utils.get_logger()


class OrderHandler:
    def __init__(self):
        self.orders = {}

    def add(self, order):
        self.orders[str(order.id)] = order

    def get(self, order_id):
        return self.orders[str(order_id)]

    def load(self, pair, exchange_name, timestamp):
        raise NotImplementedError


class CoreOrder(OrderHandler):
    def __init__(self):
        super().__init__()

    def load(self, pair, exchange_name, timestamp):
        return self._load(pair, exchange_name)

    def _load(self, pair, exchange_name):
        src, dst = pair.split('_')
        host = 'http://core:8000/prices/{}/{}'.format(src, dst)
        r = requests.get(host)
        assert r.status_code == requests.codes.ok, 'Cannot connect to core'
        data = r.json()
        order_book = data['exchanges'][exchange_name]
        if not order_book['Bids']:
            order_book['Bids'] = []
        if not order_book['Asks']:
            order_book['Asks'] = []
        return order_book


class SimulationOrder(OrderHandler):
    def __init__(self, rdb):
        super().__init__()
        self.rdb = rdb

    def load(self, pair, exchange_name, timestamp):
        # might need to change the timestamp in 10 timeframe
        # e.g: timestamp = int(timestamp/10) * 10
        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)
        key = '_'.join(map(str, [exchange_name, pair, timestamp]))
        logger.debug('Looking for order book: {}'.format(key))
        result = self.rdb.get(key)
        if not result:
            raise ValueError('Order book not found')
        order_book = json.loads(result)
        return order_book
