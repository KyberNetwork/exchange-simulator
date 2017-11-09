#!/usr/bin/python3

LIQUI_ADDRESS = 0x5b082bc7928e1fd5b757426fe7225cc7a6a75c55
BANK_ADDRESS = 0xbf6b2070264b37fd527bf3d393280d7b0401f447

OREDER_BOOK_IP = "core:8000"

LOGGER_NAME = "exchange_simulator"

EXCHANGE_NAME = "liqui"

WITHDRAW_ON_BLOCKCHAIN = True

TEMPLATE_TRANSACTION_ID = 0

DEFAULT_API_KEY = "s7kwmscu-u6myvpjh-47evo234-y2uxw61t-raxby17f"


class Token:

    def __init__(self, token, address, decimals):
        self.token = token
        self.address = address
        self.decimals = decimals

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.token


KNC = Token('knc', 0xb4ac19f6495df29f32878182be06a2f0572f9763, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)
OMG = Token('omg', 0x6b662ffde8f1d2240eb4eefa211463be0eb258a1, 18)
LIQUI_TOKENS = {"knc": KNC, "eth": ETH, "omg": OMG}

SUPPORTED_PAIR = ['BAT-ETH', 'CVC-ETH', 'DGD-ETH',  'EOS-ETH', 'ADX-ETH',
                  'FUN-ETH', 'GNT-ETH',  'KNC-ETH', 'LINK-ETH', 'MCO-ETH',
                  'OMG-ETH', 'PAY-ETH']
