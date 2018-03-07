import unittest

from simulator.balance_handler import BalanceHandler
from simulator import utils, config


class TestBalance((unittest.TestCase)):

    @classmethod
    def setUpClass(cls):
        DB_TEST = 1
        cls.rdb = utils.get_redis_db(db_no=DB_TEST)
        cls.supported_tokens = config.TOKENS.keys()
        cls.user = 'default_user'
        cls.balance_type = ['available', 'lock']
        cls.balance = BalanceHandler(cls.rdb, cls.supported_tokens)

    @classmethod
    def tearDownClass(cls):
        cls.rdb.flushdb()

    def test_balances_have_all_tokens(self):
        for b_type in self.balance_type:
            balance = self.balance.get(self.user, b_type)
            self.assertTrue(all(t in balance for t in self.supported_tokens))

    def test_deposit_positive_amount(self):
        token, amount, b_type = 'knc', 10, 'available'
        before = self.balance.get(self.user, b_type)[token]
        self.balance.deposit(self.user, token, amount, b_type)
        after = self.balance.get(self.user, b_type)[token]

        self.assertEqual(after, before + amount)

    def test_deposit_negative_amount(self):
        with self.assertRaises(AssertionError):
            self.balance.deposit(self.user, 'knc', -10, 'available')

    def test_deposit_not_supported_token(self):
        with self.assertRaises(ValueError):
            self.balance.deposit(self.user, 'invalid_token', 10, 'available')

    def test_widthdraw_excessive_amount(self):
        token, amount, b_type = 'knc', 10, 'available'
        avai_token = self.balance.get(self.user, b_type)[token]
        with self.assertRaises(ValueError):
            self.balance.withdraw(self.user, token, avai_token + amount, b_type)

        # the amount of token should remain unchange
        self.assertEqual(avai_token, self.balance.get(self.user, b_type)[token])

    def test_withdraw_full_amount(self):
        token, amount, b_type = 'knc', 10, 'available'

        amount = self.balance.get(self.user, b_type)[token]

        # withdraw an amount of token that exceed the error epsilon 1e-8
        with self.assertRaises(ValueError):
            self.balance.withdraw(self.user, token, amount + 1e-7, b_type)

        # withdraw an amount of token that within the error epsilon 1e-8
        self.balance.withdraw(self.user, token, amount + 1e-9, b_type)
        self.assertEqual(0, self.balance.get(self.user, b_type)[token])

    def test_withdraw_adequate_amount(self):
        token, amount, b_type = 'knc', 10, 'available'
        self.balance.deposit(self.user, token, amount, b_type)

        before = self.balance.get(self.user, b_type)[token]
        self.balance.withdraw(self.user, token, amount, b_type)
        after = self.balance.get(self.user, b_type)[token]

        self.assertEqual(after, before - amount)

    def test_withdraw_negative_amount(self):
        with self.assertRaises(AssertionError):
            self.balance.withdraw(self.user, 'knc', -10, 'available')

    def test_withdraw_not_supported_token(self):
        with self.assertRaises(ValueError):
            self.balance.withdraw(self.user, 'invalid_token', 10, 'available')

    def test_lock_balance(self):
        token, amount = 'knc', 10
        self.balance.deposit(self.user, token, amount, 'available')

        avai_before = self.balance.get(self.user, 'available')[token]
        lock_before = self.balance.get(self.user, 'lock')[token]

        self.balance.lock(self.user, token, amount)

        avai_after = self.balance.get(self.user, 'available')[token]
        lock_after = self.balance.get(self.user, 'lock')[token]

        self.assertEqual(avai_after, avai_before - amount)
        self.assertEqual(lock_after, lock_before + amount)

    def test_unlock_balance(self):
        token, amount = 'knc', 10
        self.balance.deposit(self.user, token, amount, 'lock')

        avai_before = self.balance.get(self.user, 'available')[token]
        lock_before = self.balance.get(self.user, 'lock')[token]

        self.balance.unlock(self.user, token, amount)

        avai_after = self.balance.get(self.user, 'available')[token]
        lock_after = self.balance.get(self.user, 'lock')[token]

        self.assertEqual(avai_after, avai_before + amount)
        self.assertEqual(lock_after, lock_before - amount)
