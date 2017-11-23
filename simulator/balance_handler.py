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
        assert amount >= 0, "invalid amount"
        key = self._key(user, balance_type)
        value = self._db.hincrbyfloat(key, token, amount)

    def withdraw(self, user, token, amount, balance_type):
        amount = float(amount)
        assert amount >= 0, "invalid amount"
        key = self._key(user, balance_type)
        value = self._db.hincrbyfloat(key, token, -amount)
        if value < -1e-18:  # rollback
            self._db.hincrbyfloat(key, token, amount)
            raise ValueError("insufficient balance")

    def lock(self, user, token, amount):
        self.withdraw(user, token, amount, 'available')
        self.deposit(user, token, amount, 'lock')

    def unlock(self, user, token, amount):
        self.withdraw(user, token, amount, 'lock')
        self.deposit(user, token, amount, 'available')

    def _key(self, user, type):
        return '_'.join(['balance', user, type]).lower()
