#!/usr/bin/python3
from unittest import mock
import constants
import json
import unittest
import exchange
import exchange_api_interface
import math


class TestDeposit(unittest.TestCase):
    def test_deposit_after_reset(self):
        exchange.reset_db()
        deposit_params = exchange_api_interface.DepositParams("kyber_liqui",
                                                              "KNC",
                                                              10.7)
        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit(deposit_params)

        balance = liqui_exchange.get_user_balance("kyber_liqui", "KNC")

        self.assertEqual(balance, 10.7)

    def test_deposit_and_withdraw(self):
        exchange.reset_db()
        deposit_params = exchange_api_interface.DepositParams("kyber_liqui",
                                                              "KNC",
                                                              10.7)
        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit(deposit_params)

        withdraw_params = exchange_api_interface.WithdrawParams("kyber_liqui",
                                                                "KNC",
                                                                5.6,
                                                                0xdeadbeef)

        liqui_exchange.withdraw(withdraw_params, False)

        balance = liqui_exchange.get_user_balance("kyber_liqui", "KNC")

        self.assertEqual(balance, 5.1)

    def test_deposit_and_withdraw_too_much(self):
        exchange.reset_db()
        deposit_params = exchange_api_interface.DepositParams("kyber_liqui",
                                                              "KNC",
                                                              10.7)
        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit(deposit_params)

        withdraw_params = exchange_api_interface.WithdrawParams("kyber_liqui",
                                                                "KNC",
                                                                50.6,
                                                                0xdeadbeef)

        ret_val = liqui_exchange.withdraw(withdraw_params, False)

        balance = liqui_exchange.get_user_balance("kyber_liqui", "KNC")

        self.assertEqual(ret_val, False)
        self.assertEqual(balance, 10.7)

    def test_deposit_and_convert_to_ETH(self):
        exchange.reset_db()

        # deposit
        deposit_params = exchange_api_interface.DepositParams("kyber_liqui",
                                                              "KNC",
                                                              11)
        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit(deposit_params)

        # execute order
        trade_params = exchange_api_interface.TradeParams("kyber_liqui",
                                                          "KNC",
                                                          "ETH",
                                                          5,
                                                          0.03)
        ret_val = liqui_exchange.execute_trade(trade_params)

        # get ETH balance
        balance = liqui_exchange.get_user_balance("kyber_liqui", "ETH")
        self.assertEqual(balance, 0.15)

        # get KNC balance
        balance = liqui_exchange.get_user_balance("kyber_liqui", "KNC")
        self.assertEqual(balance, 6)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://13.229.54.28:8000/prices/omg/eth':
        with open('test_exchange_data1.json') as json_file:
            json_data = json.load(json_file)
        return MockResponse(json_data, 200)

    return MockResponse(None, 404)


@mock.patch('requests.get', side_effect=mocked_requests_get)
class TestOrderBook(unittest.TestCase):

    def testLoadOk(self, mock_get):
        order_book = exchange.OrderBook(constants.OREDER_BOOK_IP,
                                        "OMG", "ETH", "liqui")
        omg, eth = order_book.execute_trade(100, 0.01)
        # you want to sell omg to eth so use exchange BuyPrices
        self.assertEqual(order_book.price_type, exchange.OrderBook.BUY)
        self.assertEqual(len(order_book.order_book), 57)
        self.assertEqual(omg, 100)
        self.assertEqual(eth, 2.5420361048832887)

        order_book = exchange.OrderBook(constants.OREDER_BOOK_IP,
                                        "ETH", "OMG", "liqui")
        eth, omg = order_book.execute_trade(100, 0.05)
        # you want to buy omg by eth so use exchange SellPrices
        self.assertEqual(order_book.price_type, exchange.OrderBook.SELL)
        self.assertEqual(len(order_book.order_book), 101)
        self.assertEqual(omg, 100)
        self.assertEqual(eth, 2.691324197095758)

    def testLoadNotOk(self, mock_get):
        order_book = exchange.OrderBook("localhost:1234",
                                        "OMG", "ETH", "liqui")
        self.assertEqual(order_book.order_book, [])

    def testRequestInvalidRate(self, mock_get):
        order_book = exchange.OrderBook(constants.OREDER_BOOK_IP,
                                        "OMG", "ETH", "liqui")
        omg, eth = order_book.execute_trade(100, 0.05)
        self.assertEqual(omg, 0)
        self.assertEqual(eth, 0)

        order_book = exchange.OrderBook(constants.OREDER_BOOK_IP,
                                        "ETH", "OMG", "liqui")
        eth, omg = order_book.execute_trade(100, 0.01)
        self.assertEqual(omg, 0)
        self.assertEqual(eth, 0)

    def testRequestInvalidQuantity(self, mock_test):
        order_book = exchange.OrderBook(constants.OREDER_BOOK_IP,
                                        "OMG", "ETH", "liqui")
        omg, eth = order_book.execute_trade(-100, 0.01)
        self.assertEqual(omg, 0)
        self.assertEqual(eth, 0)


if __name__ == '__main__':
    unittest.main()
