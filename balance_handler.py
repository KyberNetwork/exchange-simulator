class BalanceHandler:
    SUPPORTED_TOKEN = ['knc', 'eth', 'omg']

    def __init__(self, db):
        self._db = db

    def get(self, user):
        key = '_'.join(['balance', user])
        saved_balance = self._db.hgetall(key)
        if not saved_balance:
            balance = {token: 0.0 for token in type(self).SUPPORTED_TOKEN}
            self._db.hmset(key, balance)
        else:
            balance = {
                token: float(amount) for token, amount in saved_balance.items()
            }
        return balance

    def deposit(self, user, token, amount):
        amount = float(amount)
        assert amount >= 0, "invalid amount"
        key = '_'.join(['balance', user])
        value = self._db.hincrbyfloat(key, token, amount)

    def withdraw(self, user, token, amount):
        amount = float(amount)
        assert amount >= 0, "invalid amount"
        key = '_'.join(['balance', user])
        value = self._db.hincrbyfloat(key, token, -amount)
        if value < 0:
            # rollback
            self._db.hincrbyfloat(key, token, amount)
            raise ValueError("insufficient balance")
