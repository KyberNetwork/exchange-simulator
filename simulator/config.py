#!/usr/bin/python3
import sys
import os
import json
import logging
import logging.config

import yaml


class Token:

    def __init__(self, token, address, decimals):
        self.token = token
        self.address = address
        self.decimals = decimals

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.token


def get_int(hex_str):
    return int(hex_str, 16)


MODE = os.environ.get('KYBER_ENV', 'dev')
try:
    with open('config.yml', 'r') as f:
        cfg = yaml.load(f)

        logging.config.dictConfig(cfg['logging'])

        DELAY = cfg[MODE]['delay']
        BLOCKCHAIN_URL = cfg[MODE]['blockchain_url']

        try:
            with open(cfg[MODE]['addresses'], 'r') as f:
                addr = json.loads(f.read())

                EXCHANGES_ADDRESS = addr['exchangesAddress']
                for k, v in EXCHANGES_ADDRESS.items():
                    EXCHANGES_ADDRESS[k] = get_int(v)

                BANK_ADDRESS = get_int(addr['bank'])
                SUPPORTED_TOKENS = {}
                for name, token in addr['tokens'].items():
                    name = name.lower()
                    SUPPORTED_TOKENS[name] = Token(name,
                                                   get_int(token['address']),
                                                   token['decimals'])
        except FileNotFoundError as e:
            sys.exit('Deployment file is missing.')

except FileNotFoundError:
    sys.exit('Config file is missing.')


EXCHANGE_INFO = {}
for exchange in ['binance', 'bittrex', 'huobi']:
    with open("info/{}.json".format(exchange), 'r') as f:
        EXCHANGE_INFO[exchange] = json.loads(f.read())


SECRET = b'vtHpz1lUQTwUTz5p6VrxcEslF4KnDI21s1'
LOGGER_NAME = "simulator"
EXCHANGE_NAME = "liqui"

API_KEY = {
    'liqui': 's7kwmscu-u6myvpjh-47evo234-y2uxw61t-raxby17f',
    'binance': 'bbpcycmIbqJmudPrqeDzrt9CkY7nnl2ljvpRJ8CVenhejyhsyTBKQJ76BlDflR1K',
    'bittrex': '665ab1c6a04d4e4b855bd13639520c0a',
    'huobi': '48c32ba6-a86f961a-48fa19f1-bdbdc'
}

PRIVATE_KEY = {
    'bittrex': '7e72df544ce569ccd35b53a2e8411aaefebad8bb42b2ef443593663b1979ac9b',
    'liqui': '96cc6fb5cd1266f36d3c180bce8c5e4c34bd7577cad6a21fa4d59fb8589d8c28',
    'huobi': '628fee3875f87594b24c773ca410c5e5e25ad142bf2eef5ea9fc56018064fbad',
    'binance': 'cf0994187eedbeb765dd931372b75d542fd121577911486605352b32c1764b1e',
    'bitfinex': 'be0a3d742ee009b1cc7e69abcaa4dc9a5960a4bcbe0c55a11b1333826bcc13cc'
}

INITIAL_BALANCE = {
    'bittrex': {
        'eth': 125,
        'omg': 69.25,
        'knc': 400.0,
        'eos': 125.0,
        'salt': 156.25,
        'snt': 4462.5
    },
    'huobi': {
        'eth': 125,
        'omg': 69.25,
        'knc': 400.0,
        'eos': 125.0,
        'salt': 156.25,
        'snt': 4462.5
    },
    'binance': {
        'eth': 125,
        'omg': 69.25,
        'knc': 400.0,
        'eos': 125.0,
        'salt': 156.25,
        'snt': 4462.5
    }
}
