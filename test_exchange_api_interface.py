import unittest
import constants
import exchange_api_interface

liqui_int = exchange_api_interface.LiquiApiInterface()

#
# TO EXCHANGE TESTS
#


args_to_test1_1 = {
    "testdata1": "testvalue1",
    "testdata2": "testvalue2",
    "testdata3": "testvalue3",
    "testdata4": "testvalue4",
    "testdata5": "testvalue5",
    "api_key": "FDfasdfa134",
    "rate": 0.1,
    "amount": 1.2,
    "type": "sell",
    "pair": "knc_eth"
}

args_to_test1_2 = {
    "testdata1": "testvalue1",
    "testdata2": "testvalue2",
    "testdata3": "testvalue3",
    "testdata4": "testvalue4",
    "testdata5": "testvalue5",
    "api_key": "FDfasdfa134",
    "rate": 1,
    "amount": 1.2,
    "type": "sell",
    "pair": "knc_eth"
}
args_to_test1_3 = {
    "testdata1": "testvalue1",
    "testdata2": "testvalue2",
    "testdata3": "testvalue3",
    "testdata4": "testvalue4",
    "testdata5": "testvalue5",
    "api_key": "FDfasdfa134",
    "rate": 0.1,
    "amount": 1.2,
    "type": "sell",
    "pair": "omg_eth"
}
args_to_test2_1 = {
    "testdata1": "testvalue1",
    "testdata2": "testvalue2",
    "testdata3": "testvalue3",
    "api_key": "FDfasdfa134",
    "rate": 0.1111111111111,
    "amount": 1.2,
    "type": "buy",
    "pair": "knc_eth"
}

args_to_test2_2 = {
    "testdata1": "testvalue1",
    "testdata2": "testvalue2",
    "testdata3": "testvalue3",
    "api_key": "FDfasdfa134",
    "rate": 0.1111111111111,
    "amount": 1.222222222222222,
    "type": "sell",
    "pair": "knc_eth"
}
list1 = ["api_key", "type", "rate", "amount", "pair"]

result_to_test2_2 = {

    "api_key": "fdfasdfa134",
    "rate": 0.11111111,
    "qty": 1.22222222,
    "buy": False,
    "src_token": constants.KNC,
    "dst_token": constants.ETH
}

result_to_test2_1 = {
    "api_key": "fdfasdfa134",
    "rate": 0.11111111,
    "qty": 1.2,
    "buy": True,
    "src_token": constants.ETH,
    "dst_token": constants.KNC
}


class TestToExchange(unittest.TestCase):

    def setUp(self):
        self.valid_params = {
            "api_key": "FDfasdfa134",
            "rate": 0.1111111111111,
            "amount": 1.2,
            "type": "buy",
            "pair": "knc_eth"
        }

    def test_translate_args_with_lacking_of_required_params(self):
        self.valid_params.pop('amount', None)
        with self.assertRaisesRegex(ValueError,
                                    "Invalid parameters in post request"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_over_size_params(self):
        # making len(params) > 10
        self.valid_params.update({i: i for i in range(10)})
        with self.assertRaisesRegex(ValueError,
                                    "Invalid parameters in post request"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_nonce(self):
        # test with value which cannot cast to int
        self.valid_params["nonce"] = 'invalid'
        with self.assertRaisesRegex(ValueError,
                                    "invalid literal for int()"):
            liqui_int.translate_args(self.valid_params, list1)

        # test with non positive nonce
        self.valid_params["nonce"] = 0
        with self.assertRaisesRegex(ValueError, "Invalid nonce: 0"):
            liqui_int.translate_args(self.valid_params, list1)

        # test with big nonce
        self.valid_params["nonce"] = 2 ** 32
        with self.assertRaisesRegex(ValueError, "Invalid nonce: 4294967296"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_pair(self):
        self.valid_params["pair"] = "invalid_pair"
        with self.assertRaisesRegex(ValueError, "Invalid pair"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_coin_name(self):
        self.valid_params["coinname"] = "invalid_coinname"
        with self.assertRaisesRegex(ValueError, "Invalid coinname"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_rate(self):
        # test with value which cannot cast to float
        self.valid_params["rate"] = 'invalid'
        with self.assertRaisesRegex(ValueError,
                                    "could not convert string to float"):
            liqui_int.translate_args(self.valid_params, list1)

        # test with non positive float
        self.valid_params["rate"] = 0
        with self.assertRaisesRegex(ValueError, "Invalid rate: 0"):
            liqui_int.translate_args(self.valid_params, list1)

        # test with rate which is too big
        self.valid_params["rate"] = 1e6
        with self.assertRaisesRegex(ValueError, "Invalid rate: 1000000"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_address(self):
        # test with value which cannot cast to init
        self.valid_params["address"] = 'invalid_address'
        with self.assertRaisesRegex(ValueError, "invalid literal for int()"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args_with_invalid_amount(self):
        # test with value which cannot cast to float
        self.valid_params["amount"] = 'invalid'
        with self.assertRaisesRegex(ValueError,
                                    "could not convert string to float"):
            liqui_int.translate_args(self.valid_params, list1)

        # test with non positive amount
        self.valid_params["amount"] = 0
        with self.assertRaisesRegex(ValueError, "Invalid amount: 0"):
            liqui_int.translate_args(self.valid_params, list1)

    def test_translate_args(self):
        self.assertEqual(liqui_int.translate_args(args_to_test2_1, list1),
                         result_to_test2_1)
        self.assertEqual(liqui_int.translate_args(args_to_test2_2, list1),
                         result_to_test2_2)


#
# FROM EXCHANGE TESTS
#


list2 = ["error_msg", "error", "balance"]
list3 = ["error_msg", "error", "order_id"]
args_from_test1_1 = exchange_api_interface.GetBalanceOutput(
    False, "", {"omg": 1.22222, "gnt": 0})
result_from_test1_1 = (False, "balance value type")
args_from_test1_2 = exchange_api_interface.GetBalanceOutput(
    False, "", {"omg": 1.22222, "gnt": -0.1})
result_from_test1_2 = (False, "balance value negative")
args_from_test1_3 = exchange_api_interface.GetBalanceOutput(
    False, "", {"omg": 1.22222, "gnt": 1.1})
result_from_test1_3 = (True, True)
args_from_test1_4 = exchange_api_interface.TradeOutput(False, "", 123)
result_from_test1_4 = (True, True)
args_from_test1_5 = exchange_api_interface.TradeOutput(False, "", 123.1)
result_from_test1_5 = (False, "order_id type")
#
result_from_test2_1 = {"success": 0, "error": "balance value type"}
result_from_test2_2 = {"success": 0, "error": "balance value negative"}
result_from_test2_3 = {"return": {"funds": {"omg": 1.22222, "gnt": 1.1}},
                       "success": 1}
result_from_test2_4 = {"return": {"order_id": 123}, "success": 1}
result_from_test2_5 = {"error": "order_id type", "success": 0}


class TestFromExchange(unittest.TestCase):

    def test_check_results(self):
        self.assertEqual(
            liqui_int.check_answers(
                args_from_test1_1, list2), result_from_test1_1)
        self.assertEqual(
            liqui_int.check_answers(
                args_from_test1_2, list2), result_from_test1_2)
        self.assertEqual(
            liqui_int.check_answers(
                args_from_test1_3, list2), result_from_test1_3)
        self.assertEqual(
            liqui_int.check_answers(
                args_from_test1_4, list3), result_from_test1_4)
        self.assertEqual(
            liqui_int.check_answers(
                args_from_test1_5, list3), result_from_test1_5)

    def test_parse_results(self):
        self.assertEqual(
            liqui_int.parse_from_exchange("getInfo", args_from_test1_1),
            result_from_test2_1
        )
        self.assertEqual(
            liqui_int.parse_from_exchange("getInfo", args_from_test1_2),
            result_from_test2_2
        )
        self.assertEqual(
            liqui_int.parse_from_exchange("getInfo", args_from_test1_3),
            result_from_test2_3
        )
        self.assertEqual(
            liqui_int.parse_from_exchange("Trade", args_from_test1_4),
            result_from_test2_4
        )
        self.assertEqual(
            liqui_int.parse_from_exchange("Trade", args_from_test1_5),
            result_from_test2_5
        )


if __name__ == "__main__":
    unittest.main()
