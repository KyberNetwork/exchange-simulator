#!/usr/bin/python3

LIQUI_ADDRESS = 0xce656971fe4fc43a0211b792d380900761b7862c
BANK_ADDRESS = 0x1213c432d9ef0dd390ff18a53fd2349049b99a9c

OREDER_BOOK_IP = "13.229.54.28:8000"

LOGGER_NAME = "exchange_simulator"

EXCHANGE_NAME = "liqui"

WITHDRAW_ON_BLOCKCHAIN = True

TEMPLATE_TRANSACTION_ID = 0


class Token:

    def __init__(self, token, address, decimals):
        self.token = token
        self.address = address
        self.decimals = decimals

    def __str__(self):
        return self.token


KNC = Token('knc', 0x744660550f19d8843d9dd5be8dc3ecf06b611952, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)

LIQUI_TOKENS = {"knc": KNC, "eth": ETH}

SUPPORTED_PAIR = ['BAT-ETH', 'CVC-ETH', 'DGD-ETH',  'EOS-ETH', 'ADX-ETH',
                  'FUN-ETH', 'GNT-ETH',  'KNC-ETH', 'LINK-ETH', 'MCO-ETH',
                  'OMG-ETH', 'PAY-ETH']
