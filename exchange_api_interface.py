#!/usr/bin/python3
class ExchangeApiInterface:

    def parse_trade_args(self, args):
        pass

    def parse_get_balance_args(self, args):
        pass

    def parse_withdraw_args(self, args):
        pass

    def parse_deposit_args(self, args):
        pass


#

class TradeParams:

    def __init__(self, api_key, src_token, dst_token, qty, rate):
        self.api_key = api_key
        self.src_token = src_token
        self.dst_token = dst_token
        self.qty = qty
        self.rate = rate


#

class GetBalanceParams:

    def __init__(self, api_key, token):
        self.api_key = api_key
        self.token = token

#


class DepositParams:

    def __init__(self, api_key, token, qty):
        self.api_key = api_key
        self.token = token
        self.qty = qty

#


class WithdrawParams:

    def __init__(self, api_key, token, qty, dst_address):
        self.api_key = api_key
        self.token = token
        self.qty = qty
        self.dst_address = dst_address


#

class LiquiApiInterface(ExchangeApiInterface):

    def __init__(self):
        self.name = "Liqui"

    def prase_trade_args(self, args):
        # TODO
        pass

    def parse_get_balance_args(self, args):
        # TODO
        pass

    def parse_withdraw_args(self, args):
        # TODO
        pass

    def parse_deposit_args(self, args):
        # TODO
        pass

#
