#!/usr/bin/python3

LIQUI_ADDRESS = 0x2a1c0e5db761b7f176705c86c4d82fb5797b1834
BANK_ADDRESS = 0xc7159686de47f2ca06fcd1e74d1b9a1a0e584259

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


KNC = Token('knc', 0x88c29c3f40b4e15989176f9546b80a1cff4a6b0d, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)
OMG = Token('omg', 0x879b5383c9e1269be9dcf73ae9740c26b91e9802, 18)
LIQUI_TOKENS = {"knc": KNC, "eth": ETH, "omg": OMG}
