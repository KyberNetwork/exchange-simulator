#!/usr/bin/python3
import redis
from threading import Thread, Lock
import web3_interface
import constants
import time
from exchange_api_interface import TradeOutput, WithdrawOutput

#


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

    def before_api(self):
        self.mutex.acquire()

    def get_user_balance(self, user_api_key, token):
        result = self.db.get(self.name + "," + str(token) + "," + user_api_key)
        if(result is None):
            return 0
        else:
            return float(result)

    def set_user_balance(self, user_api_key, token, balance):
        self.db.set(self.name + "," + str(token) + "," + user_api_key, balance)

    def get_balances_api(self, get_balance_params):
        balances = {}
        for token in self.listed_tokens:
            balance = get_user_balance(get_balance_params.api_key, token)
            balances[token] = balance
        return GetBalanceOutput(False, "no error", balances)

    def get_order_book(self, src_token, dest_token):
        return None  # TODO

    def execute_trade_api(self, trade_params):
        user_src_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.src_token)
        user_dst_balance = self.get_user_balance(trade_params.api_key,
                                                 trade_params.dst_token)
        buy = trade_params.buy

        src_qty = trade_params.qty
        if(buy):
            src_qty = src_qty * trade_params.rate
            if(user_src_balance < src_qty):
                return TradeOutput(True, "insuficient qty", 0)

        elif(user_src_balance < src_qty):
                return TradeOutput(True, "insuficient qty", 0)
        # get order book
        order_book = self.get_order_book(trade_params.src_token,
                                         trade_params.dst_token)

        # TODO - calc exactly how much to reduce from src and how much to add
        # to dest

        dst_qty = trade_params.qty * trade_params.rate
        if(buy):
            dst_qty = trade_params.qty

        # for now, just assume limit price is the price
        user_src_balance -= src_qty
        user_dst_balance += dst_qty
        self.set_user_balance(trade_params.api_key,
                              trade_params.src_token, user_src_balance)
        self.set_user_balance(trade_params.api_key,
                              trade_params.dst_token, user_dst_balance)

        return TradeOutput(False, "", 0)

    def deposit(self, api_key, token, qty):
        """
        should be called either for testing or via check_deposits.
        assumes mutex is already locked
        """
        result = False
        try:
            user_balance = self.get_user_balance(api_key,
                                                 token)
            user_balance += qty
            self.set_user_balance(api_key, token, user_balance)
            result = True
        finally:
            return result

    def check_deposits(self, api_key):
        self.mutex.acquire()
        result = False
        try:
            # check enough time passed since last deposit check
            last_check = self.db.get(self.name + "," + "last_deposit_check")

            if(last_check is None):
                last_check = 0
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
        except Exception as e:
            print(e)
            result = False
        finally:
            self.mutex.release()
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


#


rdb = redis.Redis(host='localhost', port=6379, db=0)


liqui = Exchange(
    "Liqui", [constants.KNC, constants.ETH], rdb, constants.OREDER_BOOK_IP,
                 constants.LIQUI_ADDRESS, constants.BANK_ADDRESS, 5 * 60)

#


def reset_db():
    rdb.flushdb()


#

def get_liqui_exchange():
    return liqui
