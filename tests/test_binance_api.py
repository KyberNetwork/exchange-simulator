import logging
import unittest
from unittest import mock
import json

from binance_api import api, balance_handler, rdb


class TestBinanceAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)
        balance_handler.deposit('api_key', 'omg', 10, 'available')
        cls.app = api.test_client()
        cls.headers = {
            "X-MBX-APIKEY": "api_key"
        }

    @classmethod
    def tearDownClass(cls):
        rdb.delete('balance_api_key_available')
        rdb.delete('balance_api_key_lock')

    def test_missing_key_for_authenticated_end_point(self):
        """
        expect error message appears in response
        """
        resp = self.app.get('/api/v3/account', headers={}, data={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.decode(), str({
            'code': -2015,
            'msg': 'Invalid read-key, API-key, and/or IP.'
        }))

    def test_get_depth_without_symbol(self):
        resp = self.app.get(
            '/api/v1/depth', headers=self.headers, data={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.decode(), str({
            'code': -1102,
            'msg': "Mandatory parameter 'symbol' was not sent, "
            "was empty/null, or malformed."
        }))

    def test_get_depth_with_invalid_symbol(self):
        resp = self.app.get('/api/v1/depth?symbol=invalid_token',
                            headers=self.headers, data={})
        self.assertEqual(resp.status_code, 200)
        self.assertRegex(resp.data.decode(), 'Invalid pair')

    def test_get_depth_with_valid_symbol(self):
        resp = self.app.get('/api/v1/depth?symbol=OMGETH',
                            headers=self.headers, data={})
        self.assertEqual(resp.status_code, 200)
        ob = json.loads(resp.data)
        self.assertListEqual(list(ob.keys()), ['asks', 'bids', 'lastUpdateId'])

    def test_get_balance(self):
        resp = self.app.get('/api/v3/account',
                            headers=self.headers, data={})
        balance = json.loads(resp.data)
        self.assertIn('balances', balance)

    def test_open_order(self):
        data = {
            'symbol': 'OMGETH',
            'quantity': '10',
            'price': '0.00001',
            'side': 'SELL'
        }
        resp = self.app.post('/api/v3/order',
                             headers=self.headers, query_string=data)
        result = json.loads(resp.data)
        self.assertIn('orderId', result)

    def test_get_open_orders(self):
        query = {'symbol': 'OMGETH'}
        resp = self.app.get('/api/v3/openOrders',
                            headers=self.headers, query_string=query)
        result = json.loads(resp.data)
        self.assertIsInstance(result, list)

    def test_cancel_order(self):
        # this one will stay in open orders
        data = {
            'symbol': 'OMGETH',
            'quantity': '10',
            'price': '1',  # bad price
            'side': 'SELL'
        }
        resp = self.app.post('/api/v3/order',
                             headers=self.headers, query_string=data)
        result = json.loads(resp.data)

        query = {'symbol': 'OMGETH', 'orderId': result['orderId']}
        resp = self.app.delete('/api/v3/order',
                               headers=self.headers, query_string=query)
        result = json.loads(resp.data)
        self.assertIn('orderId', result)

    def _mock_withdraw(*args, **kargs):
        return "tx_id"

    @mock.patch('simulator.exchange.Exchange.withdraw', _mock_withdraw)
    def test_withdraw(self):
        query = {
            'address': '0xc7159686de47f2ca06fcd1e74d1b9a1a0e584259',
            'asset': 'omg',
            'amount': '1'
        }
        resp = self.app.post('/wapi/v3/withdraw.html',
                             headers=self.headers, query_string=query)
        result = json.loads(resp.data)
        self.assertEqual(result['msg'], 'success')

    def test_withdraw_history(self):
        resp = self.app.get('/wapi/v3/withdrawHistory.html',
                            headers=self.headers)
        result = json.loads(resp.data)
        self.assertIn('withdrawList', result)

    def test_deposit_history(self):
        resp = self.app.get('/wapi/v3/depositHistory.html',
                            headers=self.headers)
        result = json.loads(resp.data)
        self.assertIn('depositList', result)
