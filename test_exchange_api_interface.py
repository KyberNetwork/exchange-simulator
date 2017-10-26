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

    def test_check_args(self):
        self.assertEqual(liqui_int.check_args(args_to_test1_1, list1), True)
        self.assertEqual(liqui_int.check_args(args_to_test1_2, list1), False)
        self.assertEqual(liqui_int.check_args(args_to_test1_3, list1), False)

    def test_parse_args(self):
        self.assertEqual(
            liqui_int.parse_args(
                args_to_test2_1, list1), result_to_test2_1)
        self.assertEqual(
            liqui_int.parse_args(
                args_to_test2_2, list1), result_to_test2_2)


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
result_from_test2_3 = {"results": {"funds": {"omg": 1.22222, "gnt": 1.1}},
                       "success": 1}
result_from_test2_4 = {"results": {"order_id": 123}, "success": 1}
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
