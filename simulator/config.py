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

        DEPOSIT_DELAY = cfg[MODE]['deposit_delay']
        BLOCKCHAIN_URL = cfg[MODE]['blockchain_url']

        try:
            with open(cfg[MODE]['addresses'], 'r') as f:
                addr = json.loads(f.read())

                LIQUI_ADDRESS = get_int(addr['exchanges']['liqui']['ETH'])
                BITTREX_ADDRESS = get_int(addr['exchanges']['bittrex']['ETH'])
                BINANCE_ADDRESS = get_int(addr['exchanges']['binance']['ETH'])
                BITFINEX_ADDRESS = get_int(addr['exchanges']['bitfinex']['ETH'])

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

LOGGER_NAME = "simulator"
EXCHANGE_NAME = "liqui"
DEFAULT_LIQUI_API_KEY = "s7kwmscu-u6myvpjh-47evo234-y2uxw61t-raxby17f"
DEFAULT_BINANCE_API_KEY = '3wixkht774mwnwrufv9ccsxocdawro3aiokxx77bjbkglc10ee2nhv4kys7jc07c'
