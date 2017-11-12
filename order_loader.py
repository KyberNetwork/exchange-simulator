import logging

import requests
import json

from constants import LOGGER_NAME, OREDER_BOOK_IP
import utils

logger = utils.get_logger()


class OrderLoader:
    def load_order_book(self, src_token, dst_token, exchange_name, timestamp):
        raise NotImplementedError
        # return {'BuyPrices': [], 'SellPrices': []}


class CoreLoader(OrderLoader):
    def load_order_book(self, src_token, dst_token, exchange_name, timestamp):
        self._load_order_book(src_token, dst_token, exchange_name)

    def _load_order_book(self, src_token, dst_token, exchange_name):
        try:
            host = 'http://{}/prices/{}/{}'.format(OREDER_BOOK_IP,
                                                   src_token,
                                                   dst_token)
            r = requests.get(host)
            if r.status_code == requests.codes.ok:
                data = r.json()
                order_book = data['exchanges'][exchange_name]
                return order_book

                # for type in ['BuyPrices', 'SellPrices']:
                # # sort the order by rate
                # # descending for BuyPrices, ascending for SellPrices
                # sorted(order_book[type], key=itemgetter(
                # 'Rate'), reverse=(type == 'SellPrices'))
                # # set Id for orders so we can keep track process order
                # for o in order_book[type]:
                # o["Id"] = self.order_id(o)

                # self.buy_prices = order_book['BuyPrices']
                # self.sell_prices = order_book['SellPrices']
                # self.timestamp = float(order_book['Timestamp'])
        except requests.exceptions.RequestException as e:
            logger.error('Cannot connect to core')
            return None


class SimulatorLoader(OrderLoader):
    def __init__(self, rdb):
        self.rdb = rdb

    def load_order_book(self, src_token, dst_token, exchange_name, timestamp):
        # might need to change the timestamp in 10 timeframe
        # e.g: timestamp = int(timestamp/10) * 10
        timestamp = utils.normalize_timestamp(timestamp)
        key = '_'.join(map(str, [
            exchange_name,
            src_token,
            dst_token,
            timestamp
        ]))
        logger.debug('Looking for order book: {}'.format(key))
        result = self.rdb.get(key)
        if not result:
            order_book = None
        else:
            order_book = json.loads(result)
        return order_book
