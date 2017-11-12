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
        '_'.join(['balance', user])
        self._db.hincrby(key, token, amount)
