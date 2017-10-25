#!/usr/bin/python3

LIQUI_ADDRESS = 0xdee7f99acc05b3450536fa3e4c55a646786b1e29
BANK_ADDRESS = 0xe8fa477a586a9dc171145b8b86fae4a307984c32

OREDER_BOOK_IP = "TODO"

TOKEN_TO_ADDRESS = {KNC: 0xbd46bb7cf321b4acf0a703422f4c2dd69ad0dba0,
                    ETH: 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee}


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
