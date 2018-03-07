#!/usr/bin/python3
import json
import unittest
from simulator import web3_interface
from simulator import config


@unittest.skip('need to update address and key')
class TestWeb3(unittest.TestCase):

    def test_get_balance_and_withdraw(self):
        knc = config.TOKENS['knc']
        liqui_priv_key = config.PRIVATE_KEY['liqui']
        balance0 = web3_interface.get_balances(
            config.LIQUI_ADDRESS, [knc.address])[0]

        # withdraw 2 knc to deposit address
        tx = web3_interface.withdraw(liqui_priv_key,
                                     config.LIQUI_ADDRESS,
                                     knc.address,
                                     2,
                                     config.LIQUI_ADDRESS)

        web3_interface.wait_for_tx_confirmation(tx)
        balance1 = web3_interface.get_balances(
            config.LIQUI_ADDRESS, [knc])[0]
        self.assertEqual(balance0 + 2, balance1)

        # withdraw 2 knc to dummy address
        # balance_dummy0 = web3_interface.get_balances(0xdeadbeef, [knc])[0]

        tx = web3_interface.withdraw(liqui_priv_key,
                                     config.LIQUI_ADDRESS,
                                     knc,
                                     2,
                                     0xdeadbeef)
        web3_interface.wait_for_tx_confirmation(tx)

        # balance_dummy1 = web3_interface.get_balances(0xdeadbeef, [knc])[0]
        # self.assertEqual(balance_dummy0 + 2, balance_dummy1)

        # clear deposit
        tx = web3_interface.clear_deposits(liqui_priv_key,
                                           config.LIQUI_ADDRESS, [knc], [1])
        web3_interface.wait_for_tx_confirmation(tx)

        balance2 = web3_interface.get_balances(
            config.LIQUI_ADDRESS, [knc])[0]

        self.assertEqual(balance0 + 1, balance2)


if __name__ == '__main__':
    unittest.main()
