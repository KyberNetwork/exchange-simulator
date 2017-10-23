#!/usr/bin/python3
from operator import itemgetter
from threading import Thread, Lock
import redis
import web3_interface
import constants
import requests

###############################################################################


class Exchange:
    def __init__(self, exchange_name, db, order_book_ip,
                 ethereum_deposit_address, ethereum_bank_address):
        self.name = exchange_name
        self.db = db
        self.order_book_ip = order_book_ip
        self.deposit_address = ethereum_deposit_address
        self.bank_address = ethereum_bank_address
        self.mutex = Lock()

    def get_user_balance(self, user_api_key, token):
        result = self.db.get(self.name + "," + str(token) + "," + user_api_key)
        if(result is None):
            return 0
        else:
            return float(result)

    def set_user_balance(self, user_api_key, token, balance):
        self.db.set(self.name + "," + str(token) + "," + user_api_key, balance)

    # def get_order_book(self, src_token, dest_token):
    #     return None  # TODO

    def execute_trade_under_mutex_lock(self, trade_params):
        user_src_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.src_token)
        user_dst_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.dst_token)
        if(user_src_balance < trade_params.qty):
            print("unsufficient balance to execute trade")
            print("token = " + str(trade_params.src_token))
            print("required qty = " + str(trade_params.qty))
            print("balance = " + str(user_balance))
            return False
        # get order book
        # order_book = self.get_order_book(trade_params.src_token,
        #                                  trade_params.dst_token)
        order_book = OrderBook(trade_params.source_token,
                               trade_params.dest_token)
        src_diff, dst_diff = order_book.execute_trade(trade_params.qty,
                                                      trade_params.rate)

        # for now, just assume limit price is the price
        user_src_balance -= src_diff
        user_dst_balance += dst_diff
        self.set_user_balance(trade_params.api_key,
                              trade_params.src_token, user_src_balance)
        self.set_user_balance(trade_params.api_key,
                              trade_params.dst_token, user_dst_balance)

        return True

    def execute_trade(self, trade_params):
        self.mutex.acquire()
        result = False
        try:
            result = self.execute_trade_under_mutex_lock(trade_params)
        except Exception as e:
            print(e)
            result = False
        finally:
            self.mutex.release()
            return result

    def deposit(self, deposit_params):
        self.mutex.acquire()
        result = False
        try:
            user_balance = self.get_user_balance(deposit_params.api_key,
                                                 deposit_params.token)
            user_balance += deposit_params.qty
            self.set_user_balance(deposit_params.api_key,
                                  deposit_params.token, user_balance)
            result = True
        finally:
            self.mutex.release()
            return False

    def withdraw(self, withdraw_params, withdraw_from_blockchain):
        self.mutex.acquire()
        result = False
        try:
            user_balance = self.get_user_balance(withdraw_params.api_key,
                                                 withdraw_params.token)
            if(user_balance < withdraw_params.qty):
                raise ValueError("withdraw: user balance is too low")
            user_balance -= withdraw_params.qty
            self.set_user_balance(withdraw_params.api_key,
                                  withdraw_params.token, user_balance)
            # send tokens to withdraw address
            if (withdraw_from_blockchain):
                tx = web3_interface.withdraw(self.deposit_address,
                                             constants.TOKEN_TO_ADDRESS[
                                                 withdraw_params.token],
                                             withdraw_params.qty,
                                             withdraw_params.dst_address)

                result = tx
            else:
                result = True
        except Exception as e:
            result = False
        finally:
            self.mutex.release()
            return result


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


liqui = Exchange("Liqui", rdb, constants.OREDER_BOOK_IP,
                 constants.LIQUI_ADDRESS, constants.BANK_ADDRESS)

###############################################################################


def reset_db():
    rdb.flushdb()


###############################################################################

def get_liqui_exchange():
    return liqui
