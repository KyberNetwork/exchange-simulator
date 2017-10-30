#!/usr/bin/python3

LIQUI_ADDRESS = 0x80f35d402a77f0a72d2e72e1a72997934f7a288b
BANK_ADDRESS = 0x707c5863c952012de86c7b7b8df055ac26336824

OREDER_BOOK_IP = "TODO"

LOGGER_NAME = "exchange_simulator"


class Token:

    def __init__(self, token, address, decimals):
        self.token = token
        self.address = address
        self.decimals = decimals

    def __str__(self):
        return self.token


KNC = Token('knc', 0x03b50798dcc087953a5bd2e36e6112ad1092ceed, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)

LIQUI_TOKENS = [KNC, ETH]
