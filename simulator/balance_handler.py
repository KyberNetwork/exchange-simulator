from . import utils

logger = utils.get_logger()


class BalanceHandler:

    def __init__(self, db, supported_token):
        self._db = db
        self.supported_token = supported_token

    def get(self, user, type):
        key = self._key(user, type)
        saved_balance = self._db.hgetall(key)
        if not saved_balance:
            balance = {t: 0.0 for t in self.supported_token}
            self._db.hmset(key, balance)
        else:
            balance = {t: float(amount) for t, amount in saved_balance.items()}
        return balance

    def deposit(self, user, token, amount, balance_type):
        amount = float(amount)
        assert amount >= 0, 'invalid amount: {}'.format([amount, token])
        key = self._key(user, balance_type)
        self._db.hincrbyfloat(key, token, amount)

    def withdraw(self, user, token, amount, balance_type):
        amount = float(amount)
        assert amount >= 0, 'invalid amount: {}'.format([amount, token])
        key = self._key(user, balance_type)        
        new_value = self._db.hincrbyfloat(key, token, -amount)
        if (new_value < 0) and (abs(new_value) > 1e-8):
            self._db.hincrbyfloat(key, token, amount)            
            raise ValueError('not enough {} {} in {} balance'.format(
                amount, token, balance_type))
        if (abs(new_value) < 1e-8):
            self._db.hset(key, token, 0)

    def lock(self, user, token, amount):
        self.withdraw(user, token, amount, 'available')
        self.deposit(user, token, amount, 'lock')

    def unlock(self, user, token, amount):
        self.withdraw(user, token, amount, 'lock')
        self.deposit(user, token, amount, 'available')

    def _key(self, user, type):
        return '_'.join(['balance', user, type]).lower()
