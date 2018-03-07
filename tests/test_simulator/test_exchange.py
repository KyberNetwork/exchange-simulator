import unittest
from unittest.mock import patch
import json

from simulator.exchange import Exchange
from simulator.balance_handler import BalanceHandler
from simulator.order_handler import CoreOrder
from simulator import config, utils


class TestExchange(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DB_TEST = 1
        cls.rdb = utils.get_redis_db(db_no=DB_TEST)
        supported_tokens = config.TOKENS
        cls.orders = CoreOrder()
        cls.balance = BalanceHandler(cls.rdb, supported_tokens.keys())
        cls.exchange = Exchange(
            'exchange',
            'private_key',
            list(supported_tokens.values()),
            cls.rdb,
            cls.orders,
            cls.balance,
            config.LIQUI_ADDRESS
        )

    @classmethod
    def tearDownClass(cls):
        cls.rdb.flushdb()

    def setUp(self):
        self.trade_params = {
            'api_key': 'key',
            'type': 'sell',
            'rate': '0.003257',
            'pair': 'knc_eth',
            'amount': '100',
            'timestamp': '0'
        }

    @unittest.expectedFailure
    def test_get_balance(self):
        balance = self.exchange.get_balance()

    def test_trade_with_invalid_type(self):
        self.trade_params['type'] = 'invalid_type'
        with self.assertRaises(ValueError):
            self.exchange.trade(**self.trade_params)

    def test_trade_with_invalid_pair(self):
        self.trade_params['pair'] = 'invalid pair'
        with self.assertRaises(ValueError):
            self.exchange.trade(**self.trade_params)

    def test_trade_with_empty_balance(self):
        token = 'knc'
        user = self.trade_params['api_key']
        b_type = 'available'

        avai_token = self.balance.get(user, b_type)[token]
        # withdraw all available token
        self.balance.withdraw(user, token, avai_token, b_type)

        avai_token = self.balance.get(user, b_type)[token]
        self.assertEqual(0, avai_token)

        with self.assertRaisesRegex(ValueError, 'not enough.*balance'):
            result = self.exchange.trade(**self.trade_params)

    def _mocked_order(*args, **kwargs):
        with open('tests/data/mocked_order_knc_eth.json', 'r') as json_file:
            order_book = json.loads(json_file.read())
        return order_book

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_trade_partial_filled_order(self):
        self.trade_params['rate'] = '0.00326'
        api_key = self.trade_params['api_key']
        base, quote = 'knc', 'eth'

        self.balance.deposit(api_key, base,
                             self.trade_params['amount'], 'available')

        lock_before = self.balance.get(api_key, 'lock')
        avai_before = self.balance.get(api_key, 'available')

        result = self.exchange.trade(**self.trade_params)

        lock_after = self.balance.get(api_key, 'lock')
        avai_after = self.balance.get(api_key, 'available')

        remaining = result['remaining']
        self.assertTrue(remaining > 0)
        self.assertEqual(lock_after[base], lock_before[base] + remaining)
        self.assertTrue(avai_after[quote] > avai_before[quote])

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_trade_fully_filled_order(self):
        self.trade_params['rate'] = '0.00325'
        api_key = self.trade_params['api_key']
        base, quote = 'knc', 'eth'

        self.balance.deposit(api_key, base,
                             self.trade_params['amount'], 'available')

        lock_before = self.balance.get(api_key, 'lock')
        avai_before = self.balance.get(api_key, 'available')

        result = self.exchange.trade(**self.trade_params)

        lock_after = self.balance.get(api_key, 'lock')
        avai_after = self.balance.get(api_key, 'available')

        remaining = result['remaining']
        self.assertEqual(remaining, 0)
        # not lock balance
        self.assertEqual(lock_after[base], lock_before[base])
        self.assertTrue(avai_after[quote] > avai_before[quote])

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_trade_not_filled_order(self):
        self.trade_params['rate'] = '0.00327'
        api_key = self.trade_params['api_key']
        base, quote = 'knc', 'eth'

        self.balance.deposit(api_key, base,
                             self.trade_params['amount'], 'available')

        lock_before = self.balance.get(api_key, 'lock')
        avai_before = self.balance.get(api_key, 'available')

        result = self.exchange.trade(**self.trade_params)

        lock_after = self.balance.get(api_key, 'lock')
        avai_after = self.balance.get(api_key, 'available')

        received = result['received']
        remaining = result['remaining']
        self.assertEqual(received, 0)
        self.assertTrue(lock_after[base], lock_before[base] + remaining)
        self.assertEqual(avai_after[quote], avai_before[quote])

    @unittest.expectedFailure
    def test_match_order(self):
        self.exchange._match_order()

    @unittest.expectedFailure
    def test_get_order(self):
        order = self.exchange.get_order_book()

    @unittest.expectedFailure
    def test_cancel_order(self):
        self.exchange.cancel_order()

    @unittest.expectedFailure
    def test_withdraw(self):
        self.exchange.withdraw()
