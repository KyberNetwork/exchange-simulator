import random

MAX_ORDER_ID = 2 ** 31


class Order:
    def __init__(self, pair, type, rate, amount):
        self.pair = pair
        self.type = type
        self.rate = rate
        self.original_amount = amount
        self.executed_amount = 0
        self.remaining_amount = amount
        self.id = random.randint(0, MAX_ORDER_ID)

    def status(self):
        if self.remaining_amount > 0:
            return 0
        elif self.remaining_amount == 0:
            return 1
