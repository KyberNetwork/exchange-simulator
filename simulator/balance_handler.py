from . import utils

logger = utils.get_logger()


class BalanceHandler:

    def __init__(self, db, supported_token):
        self._db = db
        self.supported_token = supported_token

    def get(self, user, type):
        key = self._key(user, type)
        balance = self._db.hgetall(key)
        return {t: float(balance.get(t, 0)) for t in self.supported_token}

    def _check_balance_params(func):
        def wrapper(self, user, token, amount, balance_type):
            if token not in self.supported_token:
                raise ValueError('Invalid token: {}'.format(token))

            amount = float(amount)
            assert amount >= 0, 'Invalid amount: {}'.format([amount, token])

            return func(self, user, token, amount, balance_type)
        return wrapper

    @_check_balance_params
    def deposit(self, user, token, amount, balance_type):
        key = self._key(user, balance_type)
        self._db.hincrbyfloat(key, token, amount)

    @_check_balance_params
    def withdraw(self, user, token, amount, balance_type):
        key = self._key(user, balance_type)
        new_value = self._db.hincrbyfloat(key, token, -amount)

        if (new_value < 0) and (abs(new_value) > 1e-8):  # rollback
            self._db.hincrbyfloat(key, token, amount)
            raise ValueError('not enough {} {} in {} balance'.format(
                amount, token, balance_type))

        if abs(new_value) < 1e-8:
            self._db.hset(key, token, 0)

    def lock(self, user, token, amount):
        self.withdraw(user, token, amount, 'available')
        self.deposit(user, token, amount, 'lock')

    def unlock(self, user, token, amount):
        self.withdraw(user, token, amount, 'lock')
        self.deposit(user, token, amount, 'available')

    def _key(self, user, type):
        return '_'.join(['balance', user, type]).lower()
