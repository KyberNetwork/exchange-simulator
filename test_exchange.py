#!/usr/bin/python3
import json
import unittest
import exchange
import exchange_api_interface
import math
import web3_interface
import constants


class TestExchangeWithoutDesposit(unittest.TestCase):

    def test_deposit_after_reset(self):
        exchange.reset_db()

        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit("kyber_liqui", constants.KNC, 10.7)

        balance = liqui_exchange.get_user_balance("kyber_liqui", constants.KNC)

        self.assertEqual(balance, 10.7)

    def test_deposit_and_withdraw(self):
        exchange.reset_db()

        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit("kyber_liqui", constants.KNC, 10.7)

        withdraw_params = exchange_api_interface.WithdrawParams("kyber_liqui",
                                                                constants.KNC,
                                                                5.6,
                                                                0xdeadbeef,
                                                                False)

        liqui_exchange.withdraw_api(withdraw_params)

        balance = liqui_exchange.get_user_balance("kyber_liqui", constants.KNC)

        self.assertEqual(balance, 5.1)

    def test_deposit_and_withdraw_too_much(self):
        exchange.reset_db()

        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit("kyber_liqui", constants.KNC, 10.7)

        withdraw_params = exchange_api_interface.WithdrawParams("kyber_liqui",
                                                                constants.KNC,
                                                                50.6,
                                                                0xdeadbeef,
                                                                False)

        ret_val = liqui_exchange.withdraw_api(withdraw_params)

        balance = liqui_exchange.get_user_balance("kyber_liqui", constants.KNC)

        self.assertEqual(ret_val.error, True)
        self.assertEqual(balance, 10.7)

    def test_deposit_and_convert_to_ETH(self):
        exchange.reset_db()

        # deposit
        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.deposit("kyber_liqui", constants.KNC, 11)

        # execute order
        trade_params = exchange_api_interface.TradeParams("kyber_liqui",
                                                          constants.KNC,
                                                          constants.ETH,
                                                          5,
                                                          0.03,
                                                          False)
        liqui_exchange.execute_trade_api(trade_params)

        # get ETH balance
        balance = liqui_exchange.get_user_balance("kyber_liqui", constants.ETH)
        self.assertEqual(balance, 0.15)

        # get KNC balance
        balance = liqui_exchange.get_user_balance("kyber_liqui", constants.KNC)
        self.assertEqual(balance, 6)


class TestExchangeWithDesposit(unittest.TestCase):

    def test_deposit_by_sending_funds(self):
        exchange.reset_db()

        contract_balance = web3_interface.get_balances(
            constants.LIQUI_ADDRESS, [constants.KNC.address])[0]
        tx = web3_interface.clear_deposits(
            constants.LIQUI_ADDRESS, [constants.KNC.address],
            [contract_balance])

        web3_interface.wait_for_tx_confirmation(tx)

        # deposit 1 KNC by withdrawing from bank
        tx = web3_interface.withdraw(constants.LIQUI_ADDRESS,
                                     constants.KNC.address,
                                     1 * (10**constants.KNC.decimals),
                                     constants.LIQUI_ADDRESS)
        web3_interface.wait_for_tx_confirmation(tx)

        liqui_exchange = exchange.get_liqui_exchange()
        liqui_exchange.check_deposits("kyber_liqui")
        # get KNC balance
        balance = liqui_exchange.get_user_balance(
            "kyber_liqui", constants.KNC)
        self.assertEqual(balance, 1)

if __name__ == '__main__':
    unittest.main()
