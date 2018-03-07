#!/usr/bin/python3
import sys
import os
import json
import logging
import logging.config
from collections import namedtuple

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


# Create config for each exchange
CexConfig = namedtuple('CexConfig', ['name', 'private_key', 'supported_tokens',
                                     'addr', 'info'])

EXCHANGES_CFG = {}


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

                TOKENS = {}
                for name, token in addr['tokens'].items():
                    name = name.lower()
                    TOKENS[name] = Token(name,
                                         get_int(token['address']),
                                         token['decimals'])
        except FileNotFoundError as e:
            sys.exit('Deployment file is missing.')

        try:
            with open(cfg[MODE]['balances'], 'r') as f:
                INITIAL_BALANCE = json.loads(f.read())
        except FileNotFoundError as e:
            sys.exit('Initial balance setting is missing.')

        for ex_name, ex_cfg in cfg['exchanges'].items():
            supported_tks = []
            for tk in ex_cfg['supported_tokens']:
                supported_tks.append(TOKENS[tk])
            with open("info/{}.json".format(ex_name), 'r') as f:
                ex_info = json.loads(f.read())

            EXCHANGES_CFG[ex_name] = CexConfig(name=ex_name,
                                               private_key=ex_cfg['pk'],
                                               supported_tokens=supported_tks,
                                               addr=EXCHANGES_ADDRESS[ex_name],
                                               info=ex_info)


except FileNotFoundError:
    sys.exit('Config file is missing.')


SECRET = b'vtHpz1lUQTwUTz5p6VrxcEslF4KnDI21s1'
LOGGER_NAME = "simulator"

API_KEY = {
    'liqui': 's7kwmscu-u6myvpjh-47evo234-y2uxw61t-raxby17f',
    'binance': 'bbpcycmIbqJmudPrqeDzrt9CkY7nnl2ljvpRJ8CVenhejyhsyTBKQJ76BlDflR1K',
    'bittrex': '665ab1c6a04d4e4b855bd13639520c0a',
    'huobi': '48c32ba6-a86f961a-48fa19f1-bdbdc'
}
