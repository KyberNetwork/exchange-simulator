#!/usr/bin/python3
import unittest
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
                        value not in constants.CURRENCIES['LIQUI']):
                    return False
            elif key == 'pair':
                if not isinstance(value, str) or (
                        value not in constants.PAIRS['LIQUI']):
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
                                {'src_token': post_args['pair'][0:3]})
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
                            {'pair': exchange_to_kn(value, 'LIQUI', constants.PAIRS)})
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

    def parse_method(self, method, args):
        method = method.lower()
        if method == 'Trade':
            'inside trade'
            self.parse_trade_args(args)
        elif method == 'getInfo':
            self.parse_get_balance_args(args)
        elif method.lower() == 'CancelOrder':
            self.parse_cancel_args(args)
        elif method.lower() == 'OrderInfo':
            self.parse_getorder_single_args(args)
        elif method.lower() == 'WithdrawCoin':
            self.parse_withdraw_args(args)
        elif method.lower() == 'ActiveOrders':
            self.parse_getorders_open_args(args)
        elif method.lower() == 'TradeHistory':
            self.parse_gethistory_args(args)
        else:
            self.exchange_actions = {'errormsg': {
                'success': 0, 'error': 'Unsupported method requested'}}
            self.exchange_actions.update({'error': True})
        return self.exchange_actions


def kn_to_exchange(pair, exchange, absolute_pairs_path):
    """Common pair to exchange pair
    :param pair: any pair in constants.PAIRS['KN'] or other absolute path of
    a pairs dictionary
    :param exchange: any key in constants.PAIRS except constants.PAIRS['KN']
    or other absolute path of a pairs dictionary
    :param absolute_pairs_path: example: constants.PAIRS  . The
    full import path of a dictionary with the pair values
     """

    def finddash(commonpair):
        """Get the first part of the common pair"""
        position = commonpair.index('-')
        return commonpair[:position]

    if pair in absolute_pairs_path['KN']:
        basecur = finddash(pair.upper())
        for i in absolute_pairs_path[exchange]:
            if i.upper().startswith(basecur) or (
                    i.upper().endswith(basecur)):
                return i

        else:
            raise ValueError('Pair is not traded at KN')


def exchange_to_kn(pair, exchange, absolute_pairs_path):
    """Exchange pair to common pair
    :param pair: any pair in format of exchanges as shown in constants.PAIRS
     or other absolute path of a pairs dictionary
    :param exchange: any key except 'KN' in constants.PAIRS or other absolute
    path of a pairs dictionary
    :param absolute_pairs_path: example: constants.PAIRS  . The
    full import path of a dictionary with the pair values
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
        position = pair.index('eth')
        return pair[:position]
    if pair in absolute_pairs_path[exchange]:
        if exchange == 'BITTREX':
            basecur = find_bit(pair)
        elif exchange == 'LIQUI':
            basecur = find_liq(pair)
        else:
            basecur = find_bi(pair)
        for i in absolute_pairs_path['KN']:
            if i.startswith(basecur.upper()):
                return i


##########################################################################
# TESTING
##########################################################################


def tparse_args(post_args, parameters):
    string_values = ['type', 'pair', 'coinname', 'address', 'api_key']
    float_values = ['rate', 'amount']
    int_values = ['nonce', 'order_id']
    cleaned_post_args = {}
    for key, value in post_args.items():
        if key in parameters:
            key = key.lower()
            if key in string_values:
                if key == 'type' and 'pair' in post_args:
                    if post_args['type'].lower() == 'sell':
                        cleaned_post_args.update(
                            {'src_token': post_args['pair'][0:3].lower()})
                        cleaned_post_args.update({'dst_token': 'eth'})
                    elif post_args['type'].lower() == 'buy':
                        cleaned_post_args.update(
                            {'dst_token': post_args['pair'][0:3].lower()})
                        cleaned_post_args.update({'src_token': 'eth'})
                if key == 'type' and value == 'sell':
                    cleaned_post_args.update({'buy': False})
                if key == 'type' and value == 'buy':
                    cleaned_post_args.update({'buy': True})
                if key == 'coinname':
                    cleaned_post_args.update({'token': value.lower()})
                if key == 'pair' and 'type' not in post_args:
                    cleaned_post_args.update({'pair': value.lower()})
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


def check_args(post_args, required_post_keys):
    """Checks the arguments passed and returns True if they are valid
    and False if they are not"""

    currencies = ['eth', 'knc', 'omg', 'dgd', 'cvc', 'mco', 'gnt',
                  'adx', 'eos', 'pay', 'bat']

    pairs = ['omg_eth', 'dgd_eth', 'cvc_eth', 'mco_eth', 'gnt_eth',
             'adx_eth', 'pay_eth', 'bat_eth', 'knc_eth', 'eos_eth']

    types = ['buy', 'sell']

    if len(post_args) > 10 or not(
            all(p in post_args for p in required_post_keys)):
        return False
    for key, value in post_args.items():
        key = key.lower()
        if not isinstance(key, str):
            return False
        elif key == 'nonce':
            if not isinstance(value, int) or (
                    value > 4294967294) or value <= 0:
                return False
        elif key == 'coinname':
            if not isinstance(value, str) or (
                    value.lower() not in currencies):
                return False
        elif key == 'pair':
            if not isinstance(value, str) or (
                    value.lower() not in pairs):
                return False
        elif key == 'type':
            if not isinstance(value, str) or (
                    value.lower() not in types):
                return False
        elif key == 'address':
            if not isinstance(value, str) or (
                    len(value) != 42) or (
                    not value.startswith('0x')):
                return False
        elif key == 'rate':
            if not isinstance(value, float) or(
                    round(value, 8) <= 0 or round(value, 8) >= 1000000):
                return False
        elif key == 'amount':
            if not isinstance(value, float) or(round(value, 8) <= 0):
                return False
        elif key == 'order_id':
            if not isinstance(value, int):
                return False
    return True


class TestingClass (unittest.TestCase):
    def test_check_args(self):
        self.assertEqual(check_args({
            'testdata1': 'testvalue1',
            'testdata2': 'testvalue2',
            'testdata3': 'testvalue3',
            'testdata4': 'testvalue4',
            'testdata5': 'testvalue5',
            'api_key': 'FDfasdfa134',
            'rate': 0.1,
            'amount': 1.2,
            'type': 'sell',
            'pair': 'omg_eth'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), True)

        self.assertEqual(check_args({
            'testdata1': 'testvalue1',
            'Api_key': 'FDfasdfa134',
            'rate': 0.1,
            'aMount': 1.1,
            'type': 'sell',
            'pair': 'OMG_ETH'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), False)

        self.assertEqual(check_args({
            'testdata1': 'testvalue1',
            'testdata2': 'testvalue2',
            'testdata3': 'testvalue3',
            'testdata4': 'testvalue4',
            'testdata5': 'testvalue5',
            'testdata6': 'testvalue6',
            'api_key': 'FDfasdfa134',
            'rate': 0.1,
            'amount': 1.2,
            'type': 'sell',
            'pair': 'omg_eth'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), False)

        self.assertEqual(check_args({
            'testdata1': 'testvalue1',
            'testdata2': 'testvalue2',
            'testdata3': 'testvalue3',
            'api_key': 'FDfasdfa134',
            'rate': 0.1,
            'amount': 1.2,
            'type': 'SEll',
            'pair': 'OMg_eth'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), True)

    def test_tparse_args(self):
        self.assertEqual(tparse_args({
            'testdata1': 'testvalue1',
            'testdata2': 'testvalue2',
            'testdata3': 'testvalue3',
            'api_key': 'FDfasdfa134',
            'rate': 0.1,
            'amount': 1.2,
            'type': 'SEll',
            'pair': 'OMg_eth'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), {
            'api_key': 'fdfasdfa134',
            'rate': 0.1,
            'qty': 1.2,
            'buy': False,
            'src_token': 'omg',
            'dst_token': 'eth'
        })

        self.assertEqual(tparse_args({
            'testdata1': 'testvalue1',
            'testdata2': 'testvalue2',
            'testdata3': 'testvalue3',
            'api_key': 'FDfasdfa134',
            'rate': 0.111111111111,
            'amount': 1.2,
            'type': 'buY',
            'pair': 'OMg_eth'
        }, ['api_key', 'type', 'rate', 'amount', 'pair']), {
            'api_key': 'fdfasdfa134',
            'rate': 0.11111111,
            'qty': 1.2,
            'buy': True,
            'src_token': 'eth',
            'dst_token': 'omg'
        })
