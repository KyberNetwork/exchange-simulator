import logging

import requests
import json

from constants import OREDER_BOOK_IP
import utils

logger = utils.get_logger()


class OrderHandler:
    def add(self, pair, exchange_name, rate, quantity):
        raise NotImplementedError

    def load(self, pair, exchange_name, timestamp):
        raise NotImplementedError


class CoreOrder(OrderHandler):

    def add(self, pair, exchange_name, rate, quantity):
        pass

    def load(self, pair, exchange_name, timestamp):
        self._load(pair, exchange_name)

    def _load(self, pair, exchange_name):
        src, dst = pair.split('_')
        host = 'http://{}/prices/{}/{}'.format(OREDER_BOOK_IP, src, dst)
        r = requests.get(host)
        assert r.status_code == requests.codes.ok, 'Cannot connect to core'
        data = r.json()
        order_book = data['exchanges'][exchange_name]
        return order_book


class SimulationOrder(OrderHandler):
    def __init__(self, rdb):
        self.rdb = rdb

    def add(self, pair, exchange_name, rate, quantity):
        pass

    def load(self, pair, exchange_name, timestamp):
        # might need to change the timestamp in 10 timeframe
        # e.g: timestamp = int(timestamp/10) * 10
        timestamp = utils.normalize_timestamp(timestamp)
        key = '_'.join(map(str, [exchange_name, pair, timestamp]))
        logger.debug('Looking for order book: {}'.format(key))
        result = self.rdb.get(key)
        if not result:
            raise ValueError('Order book not found')
        order_book = json.loads(result)
        return order_book
