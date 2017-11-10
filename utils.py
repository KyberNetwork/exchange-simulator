import logging
from logging import config
from datetime import datetime

import json
import redis

import constants


def get_redis_db():
    return redis.Redis(host='redis', port=6379, db=0)


def normalize_timestamp(t):
    # 10000 miliseconds -> 10s
    return int(t / 10000) * 10000


logger = logging.getLogger(constants.LOGGER_NAME)


def copy_order_books_to_db(ob_file, rdb):

    def load_order_books(ob_file):
        with open(ob_file, 'r')as f:
            entries = json.loads(f.read())
            for e in entries:
                # timestamp = e['Timestamp']  # this is crawled time
                for pair in e['data']:
                    base, quote = pair.lower().split('-')
                    for exchange in e['data'][pair]:
                        if exchange == 'liqui':
                            ob = e['data'][pair][exchange]
                            yield(base, quote, exchange, ob)

    order_books = load_order_books(ob_file)
    all_timestamp = set()

    for idx, ob in enumerate(order_books):
        base, quote, exchange, order_book = ob

        timestamp = order_book['Timestamp']
        all_timestamp.add(timestamp)
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

    all_timestamp = list(all_timestamp)
    all_timestamp.sort()
    first, last = all_timestamp[0] / 1000, all_timestamp[-1] / 1000

    logger.debug("First timestamp: {}".format(datetime.fromtimestamp(first)))
    logger.debug("Last timestamp: {}".format(datetime.fromtimestamp(last)))

    with open('data/time_stamps.json', 'w') as f:
        f.write(json.dumps(all_timestamp))
