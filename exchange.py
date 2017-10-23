#!/usr/bin/python3
import redis
from threading import Thread, Lock
import web3_interface
import constants
import time

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

    def get_user_balance(self, user_api_key, token):
        result = self.db.get(self.name + "," + str(token) + "," + user_api_key)
        if(result is None):
            return 0
        else:
            return float(result)

    def set_user_balance(self, user_api_key, token, balance):
        self.db.set(self.name + "," + str(token) + "," + user_api_key, balance)

    def get_order_book(self, src_token, dest_token):
        return None  # TODO

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
        order_book = self.get_order_book(trade_params.src_token,
                                         trade_params.dst_token)

        # TODO - calc exactly how much to reduce from src and how much to add
        # to dest

        # for now, just assume limit price is the price
        user_src_balance -= trade_params.qty
        user_dst_balance += trade_params.qty * trade_params.rate
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
                    [constants.TOKEN_TO_ADDRESS[token_name]
                     for token_name in self.listed_tokens])
                if(sum(balances) > 0):
                    tx = web3_interface.clear_deposits(
                        self.deposit_address,
                        [constants.TOKEN_TO_ADDRESS[token_name]
                            for token_name in self.listed_tokens],
                        balances)
                for i in range(0, len(balances)):
                    token = self.listed_tokens[i]
                    qty = balances[i]

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


#


rdb = redis.Redis(host='localhost', port=6379, db=0)


liqui = Exchange("Liqui", ["KNC", "ETH"], rdb, constants.OREDER_BOOK_IP,
                 constants.LIQUI_ADDRESS, constants.BANK_ADDRESS, 5 * 60)

#


def reset_db():
    rdb.flushdb()


#

def get_liqui_exchange():
    return liqui
