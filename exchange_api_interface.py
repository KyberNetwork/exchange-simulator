#!/usr/bin/python3
import constants


class ExchangeApiInterface:
    def parse_trade_args(self, args):
        pass

    def parse_get_balance_args(self, args):
        pass

    def parse_withdraw_args(self, args):
        pass

    def parse_deposit_args(self, args):
        pass

##########################################################################

class TradeParams:
    def __init__(self, api_key, src_token, dst_token, qty, rate, buy):
        self.api_key = api_key
        self.src_token = src_token
        self.dst_token = dst_token
        self.qty = qty
        self.rate = rate
        self.buy = buy

##########################################################################

class TradeResults:
    def __init__(self, error, errormsg, order_id):
        """
        :param error: True or False
        :param errormsg: String containing the error message
        :order_id: integer for the order ID
        """
        self.error = error
        self.errormsg = errormsg
        self.order_id = order_id

##########################################################################

class CancelTradeParams:
    def __init__(self, api_key, order_id):
        self.api_key = api_key
        self.order_id = order_id

##########################################################################

class CancelTradeResults:
    def __init__(self, error, errormsg, order_id):
        """
       :param error: True or False
       :param errormsg: String containing the error message
       :order_id: integer for the order ID
       """
        self.error = error
        self.errormsg = errormsg
        self.order_id = order_id

###########################################################################

class GetBalanceParams:
    def __init__(self, api_key):
        self.api_key = api_key

##########################################################################

class GetBalanceResults:
    def __init__(self, error, errormsg, balance):
        """
        :param error: True or False
        :param errormsg: String containing the error message
        :param balance: Dictionary with { token1: amount1, token2: amount2} where
        token1,token2 is str according to constants.py for  KN exchange and
        amount1, amount2 is round(float, 8)
        """
        self.error = error
        self.errormsg = errormsg
        self.balance = balance

##########################################################################

class DepositParams:
    def __init__(self, api_key, token, qty):
        self.api_key = api_key
        self.token = token
        self.qty = qty

##########################################################################

class WithdrawParams:
    def __init__(self, api_key, token, qty, dst_address):
        self.api_key = api_key
        self.token = token
        self.qty = qty
        self.dst_address = dst_address

##########################################################################

class WithdrawResults:
    def __init__(self, error, errormsg, transaction_id, qty):
        """
        :param error: True or False
        :param errormsg: String containing the error message
        :param transaction_id: integer, a transaction ID for the withdrawal
        :param qty: round(float, 8) with the qty withdraws
        """
        self.error = error
        self.errormsg = errormsg
        self.transaction_id = transaction_id
        self.qty = qty

##########################################################################

class GetOrderSingleParams:
    def __init__(self, api_key, order_id):
        self.api_key = api_key
        self.order_id = order_id

##########################################################################

class GetOrderSingleResults:
    def __init__(self, error, errormsg, pair, type, original_qty,
                 remaining_qty):
        """
        :param error: True or False
        :param errormsg: String containing the error message
        :param original_qty: round(float, 8) with the qty requested originally
         for execution
        :param remaining_qty: round(float, 8) with the qty remaining
         for execution (original - executed , can be same as original for now)
        :param pair: the KN formatted (constants.PAIRS['KN'] pair for which
        the order is been placed
        :param type: 'buy' or 'sell'
        """
        self.error = error
        self.errormsg = errormsg
        self.pair = pair
        self.original_qty = original_qty
        self.remaining_qty = remaining_qty
        self.type = type

##########################################################################

class GetOrdersOpenParams:
    def __init__(self, api_key):
        self.api_key = api_key

##########################################################################

class GetHistoryParams:
    def __init__(self, api_key):
        self.api_key = api_key

##########################################################################

class LiquiApiInterface(ExchangeApiInterface):
    def __init__(self):
        self.name = "Liqui"
        self.args = {}
        self.exchange_actions = {}
        self.exchange_replies = {}
        self.method_error = {}

    def check_answers(exchange_results,required_results):
        """Checks the replies from the exchange for any errors.
         :param exchange_results: is a class object generated by the
         exchange"""
        answers = vars(exchange_results)
        if len(answers) > 10 or not (
                all(p in answers for p in required_results)):
            return False, "missing required results or too many results"
        for key, value in answers.items():
            if not isinstance(key, str):
                return False, "key type"
            if key == 'error' and not isinstance(value, bool):
                return False, "error type"
            if key == 'errormsg' and not isinstance(value, str):
                return False, "error message type"
            if key == 'order_id':
                if not isinstance(value, int):
                    return False, "order_id  type"
                if 0 > value:
                    return False, "order_id value"
            if key == 'balance':
                if not isinstance(value, dict):
                    return False, "balance type"
                for k, v in value.items():
                    if not isinstance(v, float):
                        return False, "balance value type"
                    if v < 0:
                        return False, "balance value negative"
            if key == 'transaction_id':
                if not isinstance(value, int):
                    return False, "transaction id type"
                if value < 0:
                    return False, "transaction id value"
            if key == 'original_qty':
                if not isinstance(value, float):
                    return False, "original_quantity type"
                if value < 0:
                    return False, "original_quantity negative"
            if key == 'remaining_qty':
                if not isinstance(value, float):
                    return False, "remaining_quantity type"
                if value < 0:
                    return False, "remaining_quantity negative"
                if value > answers['original_qty']:
                    return False, "remaining_quantity > original_quantity"
            if key == 'type':
                if not isinstance(value, str):
                    return False, "buy/sell type"
                if value.lower() not in ['buy', 'sell']:
                    return False, "buy/sell value"
        return True

    def parse_answers(exchange_results, required_results):
        """Converts the exchange results to liqui results
         :param exchange_results: is a class object generated by the
         exchange"""
        answers = vars(exchange_results)
        replies = {"results":{}}
        for key, value in answers.items():
            if key in required_results:
                if key == 'error' and value:
                    replies["success"] = 0
                    replies["error"] = answers['errormsg']
                elif key == 'error':
                    replies["success"] = 1
                if key == 'order_id':
                    replies["results"]["order_id"] = value
                if key == 'balance':
                    funds = {}
                    for k, v in value.items():
                        funds[k.lower()] = round(v, 8)
                    replies["results"]["funds"] = funds
                if key == 'transaction_id':
                    replies["results"]["tId"] = value
                if key == 'original_qty':
                    replies["results"]["received"] = round(value, 8)
                if key == 'remaining_qty':
                    replies["results"]["remains"] = round(value, 8)
                if key == 'type':
                    replies["results"]["type"] = value.lower()
        return replies


    def check_args(post_args, required_post_keys):
        """Checks the arguments passed and returns True if they are valid
        and False if they are not"""

        types = ['buy', 'sell']

        if len(post_args) > 10 or not (
                all(p in post_args for p in required_post_keys)):
            return False
        for key, value in post_args.items():
            if not isinstance(key, str):
                return False
            elif key == 'nonce':
                if not isinstance(value, int) or (
                        value > 4294967294) or value <= 0:
                    return False
            elif key == 'coinname':
                if not isinstance(value, str) or (
                        value not in constants.LIQUI_TOKENS):
                    return False
            elif key == 'pair':
                if not isinstance(value, str) or (
                        value not in constants.LIQUI_PAIRS):
                    return False
            elif key == 'type':
                if not isinstance(value, str) or (
                        value not in types):
                    return False
            elif key == 'address':
                if not isinstance(value, str) or (
                    len(value) != 42) or (
                        not value.startswith('0x')):
                    return False
            elif key == 'rate':
                if not isinstance(value, float) or (
                    round(value, 8) <= 0 or round(value,
                                                  8) >= 1000000):
                    return False
            elif key == 'amount':
                if not isinstance(value, float) or (round(value, 8) <= 0):
                    return False
            elif key == 'order_id':
                if not isinstance(value, int):
                    return False
        return True
    check_args = staticmethod(check_args)

    def parse_args(self, post_args, parameters):
        string_values = ['type', 'pair', 'coinname', 'address', 'api_key']
        float_values = ['rate', 'amount']
        int_values = ['nonce', 'order_id']
        cleaned_post_args = {}
        for key, value in post_args.items():
            if key in parameters:
                if key in string_values:
                    if key == 'type' and 'pair' in post_args:
                        if post_args['type'] == 'sell':
                            cleaned_post_args.update(
                                {'src_token': post_args['pair'][0:3].lower()})
                            cleaned_post_args.update({'dst_token': 'eth'})
                        elif post_args['type'] == 'buy':
                            cleaned_post_args.update(
                                {'dst_token': post_args['pair'][0:3]})
                            cleaned_post_args.update({'src_token': 'eth'})
                    if key == 'type' and value == 'sell':
                        cleaned_post_args.update({'buy': False})
                    if key == 'type' and value == 'buy':
                        cleaned_post_args.update({'buy': True})
                    if key == 'coinname':
                        cleaned_post_args.update({'token': value.upper()})
                    if key == 'pair' and 'type' not in post_args:
                        cleaned_post_args.update(
                            {'pair': exchange_to_all(value, constants.LIQUI)})
                    if key == 'address':
                        cleaned_post_args.update(
                            {'dst_address': value.lower()})
                    if key == 'api_key':
                        cleaned_post_args.update(
                            {'api_key': value.lower()})
                elif key in float_values:
                    if key == 'rate':
                        cleaned_post_args.update({'rate': round(value, 8)})
                    if key == 'amount':
                        cleaned_post_args.update({'qty': round(value, 8)})
                elif key.lower() in int_values:
                    if key == 'order_id':
                        cleaned_post_args.update({'order_id': int(value)})
        return cleaned_post_args

    def parse_trade_args(self, args):
        self.args = args
        parameters = ['pair', 'type', 'rate', 'amount', 'api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_cancel_args(self, args):
        self.args = args
        parameters = ['order_id', 'api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_get_balance_args(self, args):
        self.args = args
        parameters = ['api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_withdraw_args(self, args):
        self.args = args
        parameters = ['coinname', 'address', 'amount', 'api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_getorders_open_args(self, args):
        self.args = args
        parameters = ['api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_getorder_single_args(self, args):
        self.args = args
        parameters = ['api_key', 'order_id']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_gethistory_args(self, args):
        self.args = args
        parameters = ['api_key']

        if LiquiApiInterface.check_args(self.args, parameters):
            self.exchange_actions = self.parse_args(self.args, parameters)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Invalid parameters in post request'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions

    def parse_trade_results(self, exchange_results):
        required_results = ['order_id','error','errormsg']
        answers = vars(exchange_results)
        check = LiquiApiInterface.check_answers(exchange_results,
                                                required_results)
        if not check[0]:
             return {"success": 0, "error":check[1]}
        else:
             return LiquiApiInterface.parse_answers(exchange_results,
                                                    required_results)

    def parse_get_balance_results(self, exchange_results):
        required_results = ['balance', 'error', 'errormsg']
        check = LiquiApiInterface.check_answers(exchange_results,
                                                required_results)
        if not check[0]:
             return {"success": 0, "error":check[1]}
        else:
             return LiquiApiInterface.parse_answers(exchange_results,
                                                    required_results)

    # parse_cancel_results(self, exchange_results)
    # parse_getorder_single_results(self, exchange_results)
    # parse_withdraw_results(self, exchange_results)
    # parse_getorders_open_results(self, exchange_results)
    # parse_gethistory_results(self, exchange_results)

    def parse_method(self, method, args):
        if method == 'Trade':
            self.parse_trade_args(args)
        elif method == 'getInfo':
            self.parse_get_balance_args(args)
        elif method == 'CancelOrder':
            self.parse_cancel_args(args)
        elif method == 'OrderInfo':
            self.parse_getorder_single_args(args)
        elif method == 'WithdrawCoin':
            self.parse_withdraw_args(args)
        elif method == 'ActiveOrders':
            self.parse_getorders_open_args(args)
        elif method == 'TradeHistory':
            self.parse_gethistory_args(args)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Unsupported method requested'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions
    
    def parse_results(self, method, exchange_results):
        if method == 'Trade':
            self.parse_trade_results(exchange_results)
        elif method == 'getInfo':
            self.parse_get_balance_results(exchange_results)
        # elif method == 'CancelOrder':
        #     self.parse_cancel_results(exchange_results)
        # elif method == 'OrderInfo':
        #     self.parse_getorder_single_results(exchange_results)
        # elif method == 'WithdrawCoin':
        #     self.parse_withdraw_results(exchange_results)
        # elif method == 'ActiveOrders':
        #     self.parse_getorders_open_results(exchange_results)
        # elif method == 'TradeHistory':
        #     self.parse_gethistory_results(exchange_results)
        # return self.exchange_actions


def all_to_exchange(pair, exchange ):
    """common pair to exchange pair
    :param pair: any pair in format of exchanges as shown in constants.py
     EXCHANGENAME_PAIRS
    :param exchange:  any object of class Exchange  in constants.py
     """

    def finddash(commonpair):
        """Get the first part of the common pair"""
        position = commonpair.index('-')
        return commonpair[:position]

    if pair in constants.ALL_PAIRS:
        basecur = finddash(pair.upper())
        for i in exchange.pairs:
            if i.upper().startswith(basecur) or (
                    i.upper().endswith(basecur)):
                return i

        else:
            raise ValueError('Pair is not a common pair')


def exchange_to_all(pair, exchange):
    """ Exchange pair to common pair
    :param pair: any pair in format of exchanges as shown in constants.py
     EXCHANGENAME_PAIRS
    :param exchange:  any object of class Exchange  in constants.py
     """

    def find_bit(pair):
        """Get the base ccy of the common pair for Bittrex"""
        position = pair.index('-')
        return pair[position + 1:]

    def find_liq(pair):
        """Get the base ccy of the common pair for Liqui"""
        position = pair.index('_')
        return pair[:position]

    def find_bi(pair):
        """Get the base ccy of the common pair for binance or bitfinex"""
        pair = pair.lower()
        position = pair.index(constants.ETH.token)
        return pair[:position]
    if pair in exchange.pairs:
        if exchange == constants.BITTREX.exchange:
            basecur = find_bit(pair)
        elif exchange == constants.LIQUI.exchange:
            basecur = find_liq(pair)
        else:
            basecur = find_bi(pair)
        for i in constants.ALL_PAIRS:
            if i.startswith(basecur.upper()):
                return i.lower()
