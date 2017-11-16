class BalanceHandler:

    def __init__(self, db, supported_token):
        self._db = db
        self.supported_token = supported_token

    def get(self, user):
        key = self._key(user)
        saved_balance = self._db.hgetall(key)
        if not saved_balance:
            balance = {token: 0.0 for token in self.supported_token}
            self._db.hmset(key, balance)
        else:
            balance = {
                token: float(amount) for token, amount in saved_balance.items()
            }
        return balance

    def deposit(self, user, token, amount):
        amount = float(amount)
        assert amount >= 0, "invalid amount"
        key = self._key(user)
        value = self._db.hincrbyfloat(key, token, amount)

    def withdraw(self, user, token, amount):
        amount = float(amount)
        assert amount >= 0, "invalid amount"
        key = self._key(user)
        value = self._db.hincrbyfloat(key, token, -amount)
        if abs(value) < 1e-8:
            # rollback
            self._db.hincrbyfloat(key, token, amount)
            raise ValueError("insufficient balance")

    def _key(self, user):
        return '_'.join(['balance', user])
