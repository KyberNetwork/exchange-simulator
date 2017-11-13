#!/usr/bin/python3
import json


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


with open('deployment_kovan.json', 'r') as f:
    cfg = json.loads(f.read())
    LIQUI_ADDRESS = get_int(cfg['exchanges']['Liqui'])
    BANK_ADDRESS = get_int(cfg['bank'])
    SUPPORTED_TOKENS = {}
    for name, token in cfg['tokens'].items():
        SUPPORTED_TOKENS[name.lower()] = Token(
            name.lower(), get_int(token['address']), token['decimals'])

ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)
SUPPORTED_TOKENS['eth'] = ETH

LOGGER_NAME = "exchange_simulator"

EXCHANGE_NAME = "liqui"

DEFAULT_API_KEY = "s7kwmscu-u6myvpjh-47evo234-y2uxw61t-raxby17f"
