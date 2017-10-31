#!/usr/bin/python3

LIQUI_ADDRESS = 0xce656971fe4fc43a0211b792d380900761b7862c
BANK_ADDRESS = 0x1213c432d9ef0dd390ff18a53fd2349049b99a9c

OREDER_BOOK_IP = "TODO"

LOGGER_NAME = "exchange_simulator"


class Token:

    def __init__(self, token, address, decimals):
        self.token = token
        self.address = address
        self.decimals = decimals

    def __str__(self):
        return self.token


KNC = Token('knc', 0x744660550f19d8843d9dd5be8dc3ecf06b611952, 18)
ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)

LIQUI_TOKENS = [KNC, ETH]
