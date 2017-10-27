import unittest
from unittest import mock
import json

import restful_api
import exchange


class TestRestfulAPI(unittest.TestCase):

    def setUp(self):
        exchange.reset_db()
        restful_api.app.testing = True
        self.app = restful_api.app.test_client()
        self.valid_headers = {
            "key": "api_key"
        }

    def tearDown(self):
        pass

    def test_missing_key_in_headers(self):
        """
        expect "error Missing Key Header" appears in response
        """
        resp = self.app.post('/liqui/method', headers={}, data={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), {
            "success": 0,
            "error": "Missing 'Key' Header"
        })

    def test_invalid_data_format(self):
        """
        expect "Invalid data format ..." appears in response
        """
        resp = self.app.post('/liqui/method', headers=self.valid_headers)
        self.assertEqual(json.loads(resp.data), {
            "success": 0,
            "error": "Invalid data format in your request"
        })

    def test_invalid_parameters(self):
        data = {
            "invalid_key": ""
        }
        resp = self.app.post('/liqui/Trade',
                             headers=self.valid_headers,
                             data=json.dumps(data))
        self.assertEqual(json.loads(resp.data), {
            "success": 0,
            "error": "Invalid parameters in post request"
        })

    """
    @mock.patch("restful_api.exchange_parser.parse_from_exchange",
                side_effect="trade_response")
    def test_trade(self, mock_get):
        data = {
            "pair": "knc_eth",
            "type": "buy",
            "rate": 1.1,
            "amount": 2.2,
        }
        resp = self.app.post('/liqui/Trade',
                             headers=self.valid_headers,
                             data=json.dumps(data))
        self.assertEqual(json.loads(resp.data), "trade_response")

    @mock.patch("restful_api.exchange_parser.parse_from_exchange",
                side_effect="withdraw_response")
    def test_withdraw_coin(self, mock_get):
        data = {
            "coinname": "ETH",
            "address": 1,
            "amount": 2.2
        }
        resp = self.app.post('/liqui/WithdrawCoin',
                             headers=self.valid_headers,
                             data=json.dumps(data))
        self.assertEqual(json.loads(resp.data), "withdraw_response")
    """

    def mock_balance_response(*args, **kargs):
        return "balance_response"

    @mock.patch("restful_api.exchange_parser.parse_from_exchange",
                side_effect=mock_balance_response)
    def test_get_info(self, mock_get):
        data = {}
        resp = self.app.post('/liqui/getInfo',
                             headers=self.valid_headers,
                             data=json.dumps(data))
        self.assertEqual(json.loads(resp.data), "balance_response")


if __name__ == '__main__':
    unittest.main()
