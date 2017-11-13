#!/usr/bin/python3

LIQUI_ADDRESS = 0x2a1c0e5db761b7f176705c86c4d82fb5797b1834
BANK_ADDRESS = 0xc7159686de47f2ca06fcd1e74d1b9a1a0e584259

LOGGER_NAME = "exchange_simulator"

EXCHANGE_NAME = "liqui"

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


ETH = Token('eth', 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 18)
KNC = Token('knc', 0x88c29c3f40b4e15989176f9546b80a1cff4a6b0d, 18)
OMG = Token('omg', 0x879b5383c9e1269be9dcf73ae9740c26b91e9802, 18)
DGD = Token('dgd', 0xc94c72978bdcc50d763a541695d90a8416f050b2, 9)
CVC = Token('cvc', 0x91cacf7aea3b0d945a2873eff7595cb4de0d7297, 8)
MCO = Token('mco', 0xb3ca241e04f2b9a94b58c9857ce854bd56efc8ee, 8)
GNT = Token('gnt', 0xee45f2ff517f892e8c0d16b341d66f14a1372cff, 18)
ADX = Token('adx', 0xf15f87db547796266cb33da7bd52a9aae6055698, 4)
PAY = Token('pay', 0xda0e5f258734959982d58f3b17457f104d6dcb68, 18)
BAT = Token('bat', 0xc12e72373eae8f3b901f6d47b7124e025e55fb2b, 18)
EOS = Token('eos', 0x44fb6a08ad67ac0b4ef57519de84bda74f99d0f6, 18)

SUPPORTED_TOKENS = {'knc': KNC, 'eth': ETH, 'omg': OMG, 'dgd': DGD,
                    'cvc': CVC, 'mco': MCO, 'gnt': GNT, 'adx': ADX,
                    'pay': PAY, 'bat': BAT, 'eos': EOS}
