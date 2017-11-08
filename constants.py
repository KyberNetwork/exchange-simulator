#!/usr/bin/python3

LIQUI_ADDRESS = 0x47a0fcb00ce27b30b20b6adfe01cba457f3ce739
BANK_ADDRESS = 0xcfd72f117fb5667dc1ac96a64e43ab700032fe51

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


KNC = Token('knc', 0x7a8957d092f2ff1342f21b500f62922238691f83, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)

LIQUI_TOKENS = {"knc": KNC, "eth": ETH}

SUPPORTED_PAIR = ['BAT-ETH', 'CVC-ETH', 'DGD-ETH',  'EOS-ETH', 'ADX-ETH',
                  'FUN-ETH', 'GNT-ETH',  'KNC-ETH', 'LINK-ETH', 'MCO-ETH',
                  'OMG-ETH', 'PAY-ETH']
