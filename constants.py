#!/usr/bin/python3

LIQUI_ADDRESS = "F3019C224501ED2D8881D0896026d144E5e5D353"
BANK_ADDRESS = 0x7ffdb79da310995b0d5778b87f69a1340b639266


class Token:
    def __init__(self, token):
        self.token = token


class Exchange:
    def __init__(self, exchange, pairs, tokens):
        self.exchange = exchange
        self.pairs = pairs
        self.tokens = tokens


ALL_PAIRS = ['OMG-ETH', 'DGD-ETH', 'CVC-ETH', 'FUN-ETH', 'MCO-ETH',
             'GNT-ETH', 'ADX-ETH', 'PAY-ETH', 'BAT-ETH', 'KNC-ETH',
             'EOS-ETH', 'LINK-ETH']

BITTREX_PAIRS = ['ETH-OMG', 'ETH-DGD', 'ETH-CVC', 'ETH-FUN', 'ETH-MCO',
                 'ETH-GNT', 'ETH-ADX', 'ETH-PAY', 'ETH-BAT']

LIQUI_PAIRS = ['omg_eth', 'dgd_eth', 'cvc_eth', 'mco_eth', 'gnt_eth',
               'adx_eth', 'pay_eth', 'bat_eth', 'knc_eth', 'eos_eth']

BINANCE_PAIRS = ['OMGETH', 'FUNETH', 'MCOETH', 'KNCETH', 'EOSETH', 'LINKETH']

BITFINEX_PAIRS = ['omgeth', 'eoseth']


ALL_TOKENS = ['OMG', 'ETH', 'DGD', 'CVC', 'FUN', 'MCO', 'GNT', 'ADX',
              'PAY', 'BAT', 'KNC', 'EOS', 'LINK']

BITTREX_TOKENS = ['OMG', 'ETH', 'DGD', 'CVC', 'FUN', 'MCO', 'GNT', 'ADX',
                  'PAY', 'BAT']

LIQUI_TOKENS = ['omg', 'eth', 'dgd', 'cvc', 'mco',
                'gnt', 'adx', 'pay', 'bat', 'knc', 'eos']

BINANCE_TOKENS = ['OMG', 'ETH', 'FUN', 'MCO', 'KNC', 'EOS', 'LINK']

BITFINEX_TOKENS = ['omg', 'eos', 'eth']


OREDER_BOOK_IP = "TODO"

TOKEN_TO_ADDRESS = {"KNC": 0xbd46bb7cf321b4acf0a703422f4c2dd69ad0dba0,
                    "ETH": 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee}


BITTREX = Exchange('bittrex', BITTREX_PAIRS, BITTREX_TOKENS)
LIQUI = Exchange('liqui', LIQUI_PAIRS, LIQUI_TOKENS)
BINANCE = Exchange('binance', BINANCE_PAIRS, BINANCE_TOKENS)
BITFINEX = Exchange('bitfinex', BITFINEX_PAIRS, BITFINEX_TOKENS)

OMG = Token('omg')
ETH = Token('eth')
DGD = Token('dgd')
CVC = Token('cvc')
FUN = Token('fun')
MCO = Token('mco')
GNT = Token('gnt')
ADX = Token('adx')
PAY = Token('pay')
BAT = Token('bat')
KNC = Token('knc')
EOS = Token('eos')
LINK = Token('link')
