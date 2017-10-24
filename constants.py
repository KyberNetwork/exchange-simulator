#!/usr/bin/python3

LIQUI_API_KEY = "46G9R9D6-WJ77XOIP-XH9HH5VQ-A3XN3YOZ-8T1R8I8T"
LIQUI_ADDRESS = "F3019C224501ED2D8881D0896026d144E5e5D353"
BANK_ADDRESS = 0x7ffdb79da310995b0d5778b87f69a1340b639266

PAIRS = {
    'KN': ['OMG-ETH', 'DGD-ETH', 'CVC-ETH', 'FUN-ETH', 'MCO-ETH',
           'GNT-ETH', 'ADX-ETH', 'PAY-ETH', 'BAT-ETH', 'KNC-ETH',
           'EOS-ETH', 'LINK-ETH'],

    'BITTREX': ['ETH-OMG', 'ETH-DGD', 'ETH-CVC', 'ETH-FUN', 'ETH-MCO',
                'ETH-GNT', 'ETH-ADX', 'ETH-PAY', 'ETH-BAT'],

    'LIQUI': ['omg_eth', 'dgd_eth', 'cvc_eth', 'mco_eth', 'gnt_eth',
              'adx_eth', 'pay_eth', 'bat_eth', 'knc_eth', 'eos_eth'],

    'BINANCE': ['OMGETH', 'FUNETH', 'MCOETH', 'KNCETH', 'EOSETH', 'LINKETH'],

    'BITFINEX': ['omgeth', 'eoseth']
}

CURRENCIES = {
    'KN': ['OMG', 'ETH', 'DGD', 'CVC', 'FUN', 'MCO', 'GNT', 'ADX',
           'PAY', 'BAT', 'KNC', 'EOS', 'LINK'],

    'BITTREX': ['OMG', 'ETH', 'DGD', 'CVC', 'FUN', 'MCO', 'GNT', 'ADX',
                'PAY', 'BAT'],

    'LIQUI': [
        'omg',
        'eth',
        'dgd',
        'cvc',
        'mco',
        'gnt',
        'adx',
        'pay',
        'bat',
        'knc',
        'eos'],

    'BITFINEX': ['omg', 'eos', 'eth'],

    'BINANCE': ['OMG', 'ETH', 'FUN', 'MCO', 'KNC', 'EOS', 'LINK']
}

OREDER_BOOK_IP = "TODO"

TOKEN_TO_ADDRESS = {"KNC": 0xbd46bb7cf321b4acf0a703422f4c2dd69ad0dba0,
                    "ETH": 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee}
