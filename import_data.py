import logging
from logging import config
from datetime import datetime

import json
import redis

from utils import normalize_timestamp

ALLOWED_TOKEN = ['knc', 'omg']


def load_order_books(filename):
    with open(filename, 'r')as f:
        entries = json.loads(f.read())
        for e in entries:
            # timestamp = e['Timestamp']  # this is crawled time
            for pair in e['data']:
                base, quote = pair.lower().split('-')
                for exchange in e['data'][pair]:
                    if exchange == 'liqui' and base in ALLOWED_TOKEN:
                        order_book = e['data'][pair][exchange]
                        yield(base, quote, exchange, order_book)


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('exchange_simulator')

    rdb = redis.Redis(host='redis', port=6379, db=0)
    rdb.flushdb()

    order_books = load_order_books('data/sample')
    # order_books = load_order_books(
    # 'data/full_order_book_data_1510006636_to_510037765')

    all_timestamp = []

    for idx, ob in enumerate(order_books):
        base, quote, exchange, order_book = ob

        timestamp = order_book['Timestamp']
        all_timestamp.append(timestamp)
        timestamp = normalize_timestamp(timestamp)

        # handle the old format with 'BuyPrices' and 'SellPrices'
        if 'BuyPrices' in order_book:
            order_book['Bids'] = order_book['BuyPrices']
            order_book.pop('BuyPrices')
        if 'SellPrices' in order_book:
            order_book['Asks'] = order_book['SellPrices']
            order_book.pop('SellPrices')

        key = '_'.join(map(str, [exchange, base, quote, timestamp]))
        rdb.set(key, json.dumps(order_book))
        if idx % 1000 == 0:
            logger.debug('Timestamp: {}'.format(timestamp))
            logger.debug('Base-Quote: {}-{}'.format(base, quote))  # e.g OMG-ETH
            logger.debug('Exchange: {}'.format(exchange))  # e.g liqui
            logger.debug('Key: {}'.format(key))
            logger.debug('-' * 100)

    start_time = min(all_timestamp) / 1000
    end_time = max(all_timestamp) / 1000
    logger.info("Starting time: {}".format(datetime.fromtimestamp(start_time)))
    logger.info("Ending time: {}".format(datetime.fromtimestamp(end_time)))
