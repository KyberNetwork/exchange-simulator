import logging
import unittest
from unittest import mock
from unittest.mock import patch
import json

from bittrex_api import api, balance_handler, rdb


class TestBittrexAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)
        balance_handler.deposit('bittrex_key', 'omg', 10, 'available')
        balance_handler.deposit('bittrex_key', 'eth', 10, 'available')
        cls.app = api.test_client()

    @classmethod
    def tearDownClass(cls):
        rdb.delete('balance_bittrex_key_available')
        rdb.delete('balance_bittrex_key_lock')

    def test_missing_key_for_authenticated_end_point(self):
        """expect error message appears in response"""
        resp = self.app.get('/api/v1.1/account/getbalances')
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertEqual(result['message'], 'APISIGN_NOT_PROVIDED')

    def test_get_depth_without_market(self):
        """market mean the pair of QUOTE BASE"""
        data = {'type': 'both'}
        resp = self.app.get('/api/v1.1/public/getorderbook', query_string=data)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertEqual(result['message'], 'MARKET_NOT_PROVIDED')

    def test_get_depth_without_type(self):
        """type mean order book type, it could be 'buy', 'sell', or 'both'"""
        data = {'market': 'ETH-OMG'}
        resp = self.app.get('/api/v1.1/public/getorderbook', query_string=data)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertEqual(result['message'], 'TYPE_NOT_PROVIDED')

    def test_get_depth_with_invalid_market(self):
        data = {'market': 'invalid', 'nonce': 1, 'type': 'both'}
        resp = self.app.get('/api/v1.1/public/getorderbook', query_string=data)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertRegex(result['message'], 'Invalid pair')

    def test_get_depth_with_valid_market(self):
        data = {'market': 'ETH-OMG', 'nonce': 1, 'type': 'both'}
        resp = self.app.get('/api/v1.1/public/getorderbook', query_string=data)
        self.assertEqual(resp.status_code, 200)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])
        self.assertListEqual(list(result['result'].keys()), ['buy', 'sell'])

    def test_get_balance(self):
        data = {'apikey': 'bittrex_key', 'nonce': 1}
        resp = self.app.get('/api/v1.1/account/getbalances', query_string=data)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])
        self.assertIsInstance(result['result'], list)

    def test_open_order(self):
        query = {'apikey': 'bittrex_key', 'nonce': 1}
        resp = self.app.get(
            '/api/v1.1/market/getopenorders', query_string=query)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])
        self.assertIsInstance(result['result'], list)

    def _mocked_order(*args, **kwargs):
        with open('tests/data/mocked_order_omg_eth.json', 'r') as json_file:
            return json.loads(json_file.read())

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_sell_limit(self):
        query = {
            'apikey': 'bittrex_key',
            'nonce': 1,
            'market': 'ETH-OMG',
            'quantity': 1,
            'rate': 0.1
        }
        resp = self.app.get('/api/v1.1/market/selllimit', query_string=query)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_buy_limit(self):
        query = {
            'apikey': 'bittrex_key',
            'nonce': 1,
            'market': 'ETH-OMG',
            'quantity': 1,
            'rate': 0.1
        }
        resp = self.app.get('/api/v1.1/market/buylimit', query_string=query)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])

    @patch('simulator.order_handler.CoreOrder.load', _mocked_order)
    def test_cancel_order(self):
        # this one will stay in open orders
        query = {
            'apikey': 'bittrex_key',
            'nonce': 1,
            'market': 'ETH-OMG',
            'quantity': 1,
            'rate': 0.1
        }
        resp = self.app.get('/api/v1.1/market/selllimit', query_string=query)
        result = json.loads(resp.data)
        order_id = result['result']['uuid']

        query = {'apikey': 'bittrex_key', 'nonce': 1, 'uuid': order_id}
        resp = self.app.get('/api/v1.1/market/cancel', query_string=query)
        result = json.loads(resp.data)
        self.assertTrue(result['success'])

    def _mock_withdraw(*args, **kargs):
        return "tx_id"

    @mock.patch('simulator.exchange.Exchange.withdraw', _mock_withdraw)
    def test_withdraw(self):
        query = {
            'address': '0xc7159686de47f2ca06fcd1e74d1b9a1a0e584259',
            'currency': 'omg',
            'quantity': '1',
            'apikey': 'bittrex_key',
            'nonce': 1
        }
        resp = self.app.get('/api/v1.1/account/withdraw', query_string=query)
        result = json.loads(resp.data)
        self.assertEqual(result['success'], True)

    def test_withdraw_history(self):
        query = {'apikey': 'bittrex_key', 'nonce': 1}
        resp = self.app.get(
            'api/v1.1/account/getwithdrawalhistory', query_string=query)
        result = json.loads(resp.data)
        self.assertIsInstance(result['result'], list)

    def test_deposit_history(self):
        query = {'apikey': 'bittrex_key', 'nonce': 1}
        resp = self.app.get('/api/v1.1/account/getdeposithistory',
                            query_string=query)
        result = json.loads(resp.data)
        self.assertIsInstance(result['result'], list)
