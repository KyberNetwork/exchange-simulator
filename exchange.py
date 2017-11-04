#!/usr/bin/python3
import logging
import time

import requests
import redis
from operator import itemgetter
from threading import Thread, Lock

import web3_interface
import constants
from exchange_api_interface import TradeOutput, WithdrawOutput, GetBalanceOutput

#
logger = logging.getLogger(constants.LOGGER_NAME)


class Exchange:

    def __init__(self, exchange_name, listed_tokens, db,
                 ethereum_deposit_address, ethereum_bank_address,
                 deposit_delay_in_secs):
        self.name = exchange_name
        self.listed_tokens = listed_tokens
        self.db = db
        self.deposit_address = ethereum_deposit_address
        self.bank_address = ethereum_bank_address
        self.deposit_delay_in_secs = deposit_delay_in_secs
        self.mutex = Lock()
        self.order_books = {}
        self.processed_order_ids = set()

    def before_api(self, api_key):
        self.mutex.acquire()
        self.check_deposits(api_key)

    def after_api(self, api_key):
        # TODO handle api_key here
        self.mutex.release()

    def get_user_balance(self, user_api_key, token):
        key = self.name + "," + str(token) + "," + user_api_key
        result = self.db.get(key)
        if(result is None):
            return 0.0
        else:
            return float(result)

    def set_user_balance(self, user_api_key, token, balance):
        self.db.set(self.name + "," + str(token) + "," + user_api_key, balance)

    def get_balances_api(self, get_balance_params):
        balances = {}
        for token in self.listed_tokens:
            balance = self.get_user_balance(get_balance_params.api_key, token)
            balances[token] = balance
        return GetBalanceOutput(False, "no error", balances)

    def get_order_book(self, src_token, dest_token):
        """Find order book in cache using src_token and dest_token as the key
        If the order book is not found then we will create it
        If the order book is expired then we reload it
        """
        pair = "{}_{}".format(src_token, dest_token)
        order_book = self.order_books.get(pair, None)
        if not order_book:
            order_book = OrderBook(src_token, dest_token, self.name)
            self.order_books[pair] = order_book
        else:
            if order_book.expired():
                order_book.reload()
        return order_book

    def execute_trade_api(self, trade_params):
        # Check user balance for this order
        user_src_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.src_token)
        user_dst_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.dst_token)
        buy = trade_params.buy

        if buy:
            src_qty = trade_params.qty * trade_params.rate
            if user_src_balance < src_qty:
                # TODO change this code, it's ugly
                return TradeOutput(True, "insuficient qty", 0, 0, 0, {})
            else:
                order_book = self.get_order_book(trade_params.dst_token,
                                                 trade_params.src_token)
                orders = order_book.sell_prices
        else:
            src_qty = trade_params.qty
            if user_src_balance < src_qty:
                # TODO change this code, it's ugly
                return TradeOutput(True, "insuficient qty", 0, 0, 0, {})
            else:
                order_book = self.get_order_book(trade_params.src_token,
                                                 trade_params.dst_token)
                orders = order_book.buy_prices

        traded_cost = 0
        traded_quantity = 0
        required_quantity = trade_params.qty
        for order in orders:
            id = order['Id']
            logger.debug("Processing order: {}".format(order))
            if id in self.processed_order_ids:
                continue  # order is already processed, continue to next order
            rate, quantity = order['Rate'], order['Quantity']
            bad_rate = (buy and rate > trade_params.rate) or (
                (not buy) and rate < trade_params.rate)
            if bad_rate:
                break  # cant get better rate -> exist

            needed_quantity = required_quantity - traded_quantity

            min_quantity = min(quantity, needed_quantity)

            logger.debug(
                "Execute this order with quantity {}".format(min_quantity))

            traded_cost += rate * min_quantity
            traded_quantity += min_quantity
            self.processed_order_ids.add(id)
            if needed_quantity == min_quantity:
                break  # trade request has been fulfilled

        if buy:
            src_diff, dst_diff = traded_cost, traded_quantity
        else:
            src_diff, dst_diff = traded_quantity, traded_cost

        # Update user balance
        user_src_balance -= src_diff
        user_dst_balance += dst_diff
        self.set_user_balance(trade_params.api_key,
                              trade_params.src_token, user_src_balance)
        self.set_user_balance(trade_params.api_key,
                              trade_params.dst_token, user_dst_balance)
        received = traded_quantity
        remains = required_quantity - received
        if remains == 0:
            order_id = 0
        else:
            order = {'Rate': trade_params.rate, 'Quantity': remains}
            order_id = order_book.add_order(order, buy)
        balances = {}
        for token in self.listed_tokens:
            balance = self.get_user_balance(trade_params.api_key, token)
            balances[token] = balance
        return TradeOutput(False, "", order_id, received, remains, balances)

    def deposit(self, api_key, token, qty):
        """
        should be called either for testing or via check_deposits.
        """
        result = False
        user_balance = self.get_user_balance(api_key, token)
        user_balance += qty
        self.set_user_balance(api_key, token, user_balance)
        return True

    def check_deposits(self, api_key):
        result = False
        # check enough time passed since last deposit check
        last_check = self.db.get(self.name + "," + "last_deposit_check")

        if(last_check is None):
            last_check = 0
        else:
            last_check = int(last_check)

        current_time = int(time.time())

        if(current_time >= last_check + self.deposit_delay_in_secs):
            balances = web3_interface.get_balances(
                self.deposit_address,
                [token.address for token in self.listed_tokens])
            if(sum(balances) > 0):
                tx = web3_interface.clear_deposits(
                    self.deposit_address,
                    [token.address for token in self.listed_tokens],
                    balances)
            for i in range(0, len(balances)):
                token = self.listed_tokens[i]
                qty = float(balances[i]) / (10**token.decimals)

                if(not self.deposit(api_key, token, qty)):
                    raise ValueError("check_deposits: deposit failed")

            self.db.set(
                self.name + "," + "last_deposit_check", current_time)

        result = True
        return False

    def withdraw_api(self, withdraw_params):
        user_balance = self.get_user_balance(withdraw_params.api_key,
                                             withdraw_params.token)
        if(user_balance < withdraw_params.qty):
            logger.debug("User balance: {}".format(user_balance))
            logger.debug("Withdraw amount: {}".format(withdraw_params.qty))
            return WithdrawOutput(True, "insuficient balance", 0,
                                  withdraw_params.qty, {})
        user_balance -= withdraw_params.qty
        self.set_user_balance(withdraw_params.api_key,
                              withdraw_params.token, user_balance)
        # send tokens to withdraw address
        if (withdraw_params.withdraw_on_blockchain):
            tx = web3_interface.withdraw(
                self.deposit_address,
                withdraw_params.token.address,
                int(withdraw_params.qty * (10**withdraw_params.token.decimals)),
                withdraw_params.dst_address
            )
            logger.debug("Transaction: {}".format(tx))
        else:
            tx = constants.TEMPLATE_TRANSACTION_ID

        balances = {}
        for token in self.listed_tokens:
            balance = self.get_user_balance(withdraw_params.api_key, token)
            balances[token] = balance
        return WithdrawOutput(False, "", tx, withdraw_params.qty, balances)


class OrderBook:
    MAX_ORDER_ID = 2 ** 31

    def __init__(self, source_token, dest_token, exchange_name):
        self.source_token = source_token
        self.dest_token = dest_token
        self.exchange_name = exchange_name
        self.timestamp = time.time()
        self.buy_prices = []
        self.sell_prices = []

        self.load_order_book(self.source_token, self.dest_token)

    def order_id(self, o):
        """Create Id for an order by hashing a string contain
        source token, destination token, it's rate and quantity
        """
        keys = [self.source_token, self.dest_token, o['Rate'], o['Quantity']]
        return hash('.'.join(map(str, keys))) % OrderBook.MAX_ORDER_ID

    def expired(self):
        CACHE_ORDER_BOOK_TIME = 3
        return (time.time() - self.timestamp) > CACHE_ORDER_BOOK_TIME

    def reload(self):
        self.load_order_book()

    def add_order(self, order, buy):
        order["Id"] = self.order_id(order)
        if buy:
            self.buy_prices.append(order)
            sorted(self.buy_prices, key=itemgetter('Rate'), reverse=False)
        else:
            self.sell_prices.append(order)
            sorted(self.sell_prices, key=itemgetter('Rate'), reverse=True)
        return order["Id"]

    def load_order_book(self, src_token, dest_token):
        try:
            host = 'http://{}/prices/{}/{}'.format(constants.OREDER_BOOK_IP,
                                                   self.source_token,
                                                   self.dest_token)
            r = requests.get(host)
            if r.status_code == requests.codes.ok:
                data = r.json()
                order_book = data['exchanges'][self.exchange_name]
                for type in ['BuyPrices', 'SellPrices']:
                    # sort the order by rate
                    # descending for BuyPrices, ascending for SellPrices
                    sorted(order_book[type], key=itemgetter(
                        'Rate'), reverse=(type == 'SellPrices'))
                    # set Id for orders so we can keep track process order
                    for o in order_book[type]:
                        o["Id"] = self.order_id(o)

                self.buy_prices = order_book['BuyPrices']
                self.sell_prices = order_book['SellPrices']
                self.timestamp = float(order_book['Timestamp'])
        except requests.exceptions.RequestException:
            logger.error('Cannot make request to get order book')


rdb = redis.Redis(host='localhost', port=6379, db=0)


liqui = Exchange("liqui", [constants.KNC, constants.ETH], rdb,
                 constants.LIQUI_ADDRESS, constants.BANK_ADDRESS, 5 * 60)

#


def reset_db():
    rdb.flushdb()


###############################################################################

def get_liqui_exchange():
    return liqui
