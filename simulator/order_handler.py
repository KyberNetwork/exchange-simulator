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
        order_id = str(order_id)
        if order_id not in self.orders:
            raise ValueError('Order not found.')
        return self.orders[order_id]

    def get_all(self, pair=None):
        all_orders = self.orders.values()
        if not pair:
            return all_orders
        else:
            return list(filter(lambda o: o.pair == pair, all_orders))

    def remove(self, order_id):
        try:
            del self.orders[order_id]
        except KeyError:
            raise ValueError('Order not found.')

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
        order_book = data['exchanges'].get(exchange_name, None)
        if not order_book:
            raise ValueError("{}'s data is not available".format(exchange_name))
        return order_book


class SimulationOrder(OrderHandler):
    def __init__(self, rdb):
        super().__init__()
        self.rdb = rdb

    def load(self, pair, exchange_name, timestamp):
        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)
        key = '_'.join(map(str, [exchange_name, pair, timestamp]))
        logger.debug('Looking for order book: {}'.format(key))
        result = self.rdb.get(key)
        if not result:
            raise ValueError('Order book not found: {}'.format(key))
        order_book = json.loads(result)
        return order_book
