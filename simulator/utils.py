import sys
import os
import logging
import time
import uuid
from datetime import datetime
import random

import requests
import json
import redis

from . import config

logger = logging.getLogger(config.LOGGER_NAME)


def bittrex_fmt_time(t):
    dt = datetime.fromtimestamp(t / 1000)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


def get_redis_db(db_no=0):
    return redis.Redis(host='redis', port=6379, db=db_no, decode_responses=True)


def normalize_timestamp(t):
    # 10000 miliseconds -> 10s
    return int(t / 10000) * 10000


def get_logger(name=config.LOGGER_NAME):
    return logging.getLogger(name)


def get_token(name):
    if name not in config.SUPPORTED_TOKENS:
        raise ValueError('Not supported: {}'.format(name))
    return config.SUPPORTED_TOKENS[name]


def init_deposit(balance, user, tokens, amount):
    for token in tokens:
        balance.deposit(user, token, amount, 'available')
        balance.deposit(user, token, amount, 'lock')
        balance.withdraw(user, token, amount, 'lock')


def get_real_timestamp():
    return int(time.time() * 1000)


def get_timestamp(data={}):
    if config.MODE == 'simulation':
        try:
            r = requests.get('http://scheduler:7000/get')
            data = r.json()
            timestamp = data['timestamp']
        except Exception as e:
            logger.error("Can't get timestamp from scheduler: {}".format(e))
            timestamp = int(time.time() * 1000)
    else:
        timestamp = data.get('timestamp', int(time.time()) * 1000)
    return timestamp


def get_random_id():
    return random.randint(0, 10000000)


def get_random_uuid():
    return str(uuid.uuid4())


def setup_data(rdb, ob_file):
    # import simulation data
    FLAG = 'IMPORTED_SIMULATION_DATA'
    imported = rdb.get(FLAG)
    if not imported:
        logger.info('Importing simulation data ...')
        try:
            copy_order_books_to_db(ob_file, rdb)
        except FileNotFoundError:
            sys.exit('Data is missing.')
        rdb.set(FLAG, True)
        logger.info('Done.')


def copy_order_books_to_db(ob_file, rdb):
    EXCHANGES = ['liqui', 'binance', 'bittrex']

    def load_order_books(ob_file):
        with open(ob_file, 'r') as f:
            for line in f:
                e = json.loads(line)
                for pair in e['data']:
                    base, quote = pair.lower().split('-')
                    for exchange in e['data'][pair]:
                        if exchange in EXCHANGES:
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
            order_book['Asks'] = order_book['BuyPrices']
            order_book.pop('BuyPrices')
        if 'SellPrices' in order_book:
            order_book['Bids'] = order_book['SellPrices']
            order_book.pop('SellPrices')

        key = '_'.join(map(str, [exchange, base, quote, timestamp]))
        rdb.set(key, json.dumps(order_book))
        # if idx % 1000 == 0:
        # logger.debug('Timestamp: {}'.format(timestamp))
        # logger.debug('Base-Quote: {}-{}'.format(base, quote))  # e.g OMG-ETH
        # logger.debug('Exchange: {}'.format(exchange))  # e.g liqui
        # logger.debug('Key: {}'.format(key))
        # logger.debug('-' * 100)

    all_timestamp = list(all_timestamp)
    all_timestamp.sort()
    first, last = all_timestamp[0] / 1000, all_timestamp[-1] / 1000

    # logger.debug("First timestamp: {}".format(datetime.fromtimestamp(first)))
    # logger.debug("Last timestamp: {}".format(datetime.fromtimestamp(last)))

    with open('data/time_stamps.json', 'w') as f:
        f.write(json.dumps(all_timestamp))


def convert_ob_json_file(ob_json_file, new_file):
    """Convert order book json file to a new format
    """
    with open(ob_json_file, 'r') as ob_json:
        obs = json.loads(ob_json.read())
        with open(new_file, 'w') as new_f:
            for ob in obs:
                new_f.write(json.dumps(ob) + '\n')


def get_pending_tnx(exchange):
    r = requests.get('http://core:8000/immediate-pending-activities')
    data = r.json()

    logger.info('Pending response: {}'.format(data))

    activities = data.get('data', [])
    pending_deposits = {}
    for a in activities:
        if a['Destination'] != exchange:
            continue

        if (not a['Result']['error']) and (a['Action'] == 'deposit'):
            token = a['Params']['token'].lower()
            if token not in pending_deposits:
                pending_deposits[token] = []
            pending_deposits[token].append({
                'amount': a['Params']['amount'],
                'tx': a['Result']['tx']
            })
    return pending_deposits


def view_simulation_ob(exchange, base, quote, timestamp):
    rdb = get_redis_db()
    timestamp = normalize_timestamp(timestamp)
    key = '_'.join(map(str, [exchange, base, quote, timestamp]))
    ob = rdb.get(key)
    print(json.loads(ob))


if __name__ == '__main__':
    # src, dst = 'data/full_ob', 'data/full_ob.dat'
    # src, dst = 'data/sample_ob', 'data/sample_ob.dat'
    # convert_ob_json_file(src, dst)

    # import time

    # start = time.time()
    # rdb = get_redis_db()
    # copy_order_books_to_db(dst, rdb)
    # end = time.time()
    # print("Import time: {}s".format(end - start))
    view_simulation_ob('binance', 'eos', 'eth', 1510009456430)
