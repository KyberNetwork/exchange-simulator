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

    def __init__(self, exchange_name, listed_tokens, db, order_book_ip,
                 ethereum_deposit_address, ethereum_bank_address,
                 deposit_delay_in_secs):
        self.name = exchange_name
        self.listed_tokens = listed_tokens
        self.db = db
        self.order_book_ip = order_book_ip
        self.deposit_address = ethereum_deposit_address
        self.bank_address = ethereum_bank_address
        self.deposit_delay_in_secs = deposit_delay_in_secs
        self.mutex = Lock()
        self.order_book_cache = {}
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
        If the order book is not found or expired then we fetch order book
        from data fetcher
        """
        CACHE_TIME = 60 * 1

        def expired(ob):
            return (time.time() - float(ob['Timestamp'])) > CACHE_TIME

        pair = "{}_{}".format(src_token, dest_token)
        order_book = self.order_book_cache.get(pair, {"Timestamp": 0})
        if expired(order_book):
            logger.info("Fetching order book for {}".format(pair))
            order_book = self.fetch_order_book(src_token, dest_token)
            self.order_book_cache[pair] = order_book
        return order_book

    def fetch_order_book(self, src_token, dest_token):
        def set_order_id(o):
            """Create Id for an order by hashing a string contain
            source token, destination token, it's rate and quantity
            """
            keys = [src_token, dest_token, o['Rate'], o['Quantity']]
            o['Id'] = hash('.'.join(map(str, keys)))

        order_book = {
            'BuyPrices': {},
            'SellPrices': {},
            'Timestamp': time.time()
        }
        # TODO change this host
        # host = 'http://{}/prices/{}/{}'.format(constants.OREDER_BOOK_IP,
        #                                        src_token,
        #                                        dest_token)
        # currently, data fetcher only support this
        host = 'http://{}/prices/knc/eth'.format(self.order_book_ip)
        try:
            r = requests.get(host)
            if r.status_code == requests.codes.ok:
                data = r.json()
                order_book = data['exchanges'].get(self.name, order_book)
                for type in ['BuyPrices', 'SellPrices']:
                    # sort the order by rate
                    # descending for BuyPrices, ascending for SellPrices
                    sorted(order_book[type], key=itemgetter(
                        'Rate'), reverse=(type == 'SellPrices'))
                    # set Id for orders so we can keep track process order
                    [set_order_id(o) for o in order_book[type]]
            logger.debug("Buy order: {}".format(order_book['BuyPrices'][:3]))
            logger.debug("Sell order: {}".format(order_book['SellPrices'][:3]))
        except requests.exceptions.RequestException:
            logger.error('Cannot make request to get order book')
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
                return TradeOutput(True, "insuficient qty", 0)
        else:
            src_qty = trade_params.qty
            if user_src_balance < src_qty:
                return TradeOutput(True, "insuficient qty", 0)

        order_book = self.get_order_book(trade_params.src_token,
                                         trade_params.dst_token)
        if buy:
            orders = order_book['SellPrices']
        else:
            orders = order_book['BuyPrices']

        traded_cost = 0
        traded_quantity = 0
        required_quantity = trade_params.qty
        for order in orders:
            logger.debug("Process order: {}".format(order))

            id = order['Id']
            if id in self.processed_order_ids:
                continue  # order is already processed, continue to next order
            rate, quantity = order['Rate'], order['Quantity']
            bad_rate = (buy and rate > trade_params.rate) or (
                (not buy) and rate < trade_params.rate)
            if bad_rate:
                break  # cant get better rate -> exist
            needed_quantity = required_quantity - traded_quantity
            min_quantity = min(quantity, needed_quantity)
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
        return TradeOutput(False, "", 0)

    def deposit(self, api_key, token, qty):
        """
        should be called either for testing or via check_deposits.
        """
        result = False
        user_balance = self.get_user_balance(api_key,
                                             token)
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
            return WithdrawOutput(True, "insuficient balance", 0,
                                  withdraw_params.qty)
        user_balance -= withdraw_params.qty
        self.set_user_balance(withdraw_params.api_key,
                              withdraw_params.token, user_balance)
        # send tokens to withdraw address
        if (withdraw_params.withdraw_on_blockchain):
            tx = web3_interface.withdraw(self.deposit_address,
                                         withdraw_params.token.address,
                                         int(withdraw_params.qty *
                                             (10**withdraw_params.token.decimals)),
                                         withdraw_params.dst_address)

        return WithdrawOutput(False, "", 7, withdraw_params.qty)


class OrderBook:
    BUY = 'BuyPrices'
    SELL = 'SellPrices'

    def __init__(self, order_book_ip, source_token, dest_token, exchange_name):
        source_token = source_token.upper()
        dest_token = dest_token.upper()
        for pair in constants.SUPPORTED_PAIR:
            if source_token in pair and dest_token in pair:
                if pair.startswith(source_token):
                    self.price_type = OrderBook.BUY
                    self.source_token = source_token
                    self.dest_token = dest_token
                else:
                    self.price_type = OrderBook.SELL
                    self.source_token = dest_token
                    self.dest_token = source_token
                break

        host = 'http://%s/prices/%s/%s' % (order_book_ip,
                                           self.source_token,
                                           self.dest_token)
        self.load_orderbook(host.lower(), exchange_name.lower())

    def load_orderbook(self, host, exchange_name):
        def get_data(host, exchange_name):
            # TODO: wait for new api from victor, current use old one
            VALID_HTTP_RESPONSE = [200]
            try:
                r = requests.get(host)
            except requests.exceptions.RequestException:
                return {"Valid": False,
                        "reason": "Can not make request to host"}
            if r.status_code in VALID_HTTP_RESPONSE:
                market_data = r.json()
                if market_data.get("success", False):
                    if "exchanges" in market_data:
                        empty = {"Valid": True,
                                 "BuyPrices": {},
                                 "SellPrices": {}}
                        return market_data["exchanges"].get(exchange_name,
                                                            empty)
                return {"Valid": False,
                        "reason": market_data.get("reason",
                                                  "Invalid server data format")
                        }
            return {"Valid": False, "reason": "Invalid server status code"}

        def parse_orderbook(market_data):
            data = []
            if market_data["Valid"]:
                reversed_sort = (self.price_type == OrderBook.BUY)
                for command in market_data[self.price_type]:
                    data.append((command['Rate'], command['Quantity']))
                data.sort(key=itemgetter(0), reverse=reversed_sort)
            return data

        market_data = get_data(host, exchange_name)
        self.order_book = parse_orderbook(market_data)

    def execute_trade(self, required_qty, request_rate):

        def rate_exceed_threshold(rate, threshold):
            return ((rate - threshold) *
                    (-1 if self.price_type == OrderBook.BUY else 1)) > 0
        if required_qty < 0:
            return 0, 0
        total_cost = 0
        total_quantity = 0
        for command in self.order_book:
            command_rate, command_volume = command
            if rate_exceed_threshold(command_rate, request_rate):
                break
            needed_volume = required_qty - total_quantity
            if needed_volume > command_volume:
                total_cost += command_rate * command_volume
                total_quantity += command_volume
            else:
                total_cost += needed_volume * command_rate
                total_quantity += needed_volume
                break
        if self.price_type == OrderBook.BUY:
            return total_quantity, total_cost
        else:
            return total_cost, total_quantity
###############################################################################


rdb = redis.Redis(host='localhost', port=6379, db=0)


liqui = Exchange(
    "liqui", [constants.KNC, constants.ETH], rdb, constants.OREDER_BOOK_IP,
    constants.LIQUI_ADDRESS, constants.BANK_ADDRESS, 5 * 60)

#


def reset_db():
    rdb.flushdb()


###############################################################################

def get_liqui_exchange():
    return liqui
