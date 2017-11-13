#!/usr/bin/python3
import logging
import time

import requests
import redis
from threading import Thread, Lock

import web3_interface
import constants
import utils

MAX_ORDER_ID = 2 ** 31


logger = logging.getLogger(constants.LOGGER_NAME)


class Exchange:

    def __init__(self, exchange_name, supported_tokens, db,
                 order_handler, balance_handler,
                 deposit_address, bank_address,
                 deposit_delay_in_secs):
        self.name = exchange_name
        self.supported_tokens = supported_tokens
        self.db = db
        self.balance = balance_handler
        self.order = order_handler
        self.deposit_address = deposit_address
        self.bank_address = bank_address
        self.deposit_delay_in_secs = deposit_delay_in_secs
        self.mutex = Lock()
        self.processed_order_ids = set()
        self.remaining_orders = []

    def before_api(self, api_key):
        self.mutex.acquire()
        self.check_deposits(api_key)

    def after_api(self, api_key):
        # TODO handle api_key here
        self.mutex.release()

    def get_balance_api(self, api_key, *args, **kargs):
        return {
            'funds': self.balance.get(user=api_key)
        }

    def get_order_book(self, pair, timestamp):
        try:
            order_book = self.order.load(pair, self.name, timestamp)
        except Exception as e:
            logger.error(e)
            order_book = {'Asks': [], 'Bids': []}

        # logger.debug("Order Book: {}".format(order_book))
        return order_book

    def get_depth_api(self, pairs, timestamp):
        depth = {}
        pairs = pairs.split('-')
        for pair in pairs:
            order_book = self.get_order_book(pair, timestamp)
            depth[pair] = {
                "asks": [
                    [o['Rate'], o['Quantity']] for o in order_book['Asks']
                ],
                "bids": [
                    [o['Rate'], o['Quantity']] for o in order_book['Bids']
                ],
            }
        return depth

    def trade_api(self, api_key, type, rate, pair, amount,
                  timestamp, *args, **kargs):
        # lock balance for new order
        rate, amount = float(rate), float(amount)
        base, quote = pair.split('_')
        if type == 'buy':
            self.balance.withdraw(api_key, quote, rate * amount)
        elif type == 'sell':
            self.balance.withdraw(api_key, base, amount)
        else:
            raise ValueError('Invalid type of order.')
        # append new order to the unmatch orders
        unmatch_orders = self.remaining_orders
        self.remaining_orders = []
        unmatch_orders.append({
            'api_key': api_key,
            'type': type,
            'rate': rate,
            'pair': pair,
            'amount': amount,
            'timestamp': timestamp
        })

        for order in unmatch_orders:
            order['timestamp'] = timestamp  # to match order with the correct ob
            result = self._match_order(**order)
            if result['remains'] > 0:
                order['amount'] = result['remains']
                self.remaining_orders.append(order)

        # the last result is corresponding to the new order
        result['funds'] = self.balance.get(user=api_key)
        return result

    def _match_order(self, api_key, type, rate, pair, amount, timestamp):
        order_book = self.get_order_book(pair, timestamp)
        base, quote = pair.split('_')  # e.g. knc_eth -> base=knc, quote=eth
        if type == 'buy':
            orders = order_book['Asks']
        elif type == 'sell':
            orders = order_book['Bids']

        base_change = 0
        quote_change = 0
        for order in orders:
            logger.debug('Processing order: {}'.format(order))

            id = get_order_id(pair, order['Rate'], order['Quantity'])
            if id in self.processed_order_ids:
                continue  # order is already processed, continue to next order

            bad_rate = (type == 'buy' and order['Rate'] > rate) or (
                type == 'sell' and order['Rate'] < rate)
            if bad_rate:
                break  # cant get better rate -> exist

            needed_quantity = amount - base_change
            trade_amount = min(order['Quantity'], needed_quantity)

            logger.debug(
                'Execute this order with quantity {}'.format(trade_amount))

            base_change += trade_amount
            quote_change += rate * trade_amount

            self.processed_order_ids.add(id)
            if needed_quantity == trade_amount:
                break  # trade request has been fulfilled

        logger.debug('Base change, Quote change: {}, {}'.format(
            base_change, quote_change))

        # udpate balance
        if type == 'buy':
            self.balance.deposit(api_key, base, base_change)
        else:
            self.balance.deposit(api_key, quote, quote_change)

        received = base_change
        remains = amount - received

        if remains == 0:
            order_id = 0
        else:
            order_id = get_order_id(pair, rate, remains)

        return {
            'received': received,
            'remains': remains,
            'order_id': order_id
        }

    def check_deposits(self, api_key):
        # check enough time passed since last deposit check
        check_deposit_key = ','.join([self.name, 'last_deposit_check'])
        last_check = self.db.get(check_deposit_key)

        if(last_check is None):
            last_check = 0
        else:
            last_check = int(last_check)

        current_time = int(time.time())
        if(current_time >= last_check + self.deposit_delay_in_secs):
            balances = web3_interface.get_balances(
                self.deposit_address,
                [token.address for token in self.supported_tokens])

            if(sum(balances) > 0):
                tx = web3_interface.clear_deposits(
                    self.deposit_address,
                    [token.address for token in self.supported_tokens],
                    balances)

            for idx, balance in enumerate(balances):
                token = self.supported_tokens[idx]
                qty = float(balance) / (10**token.decimals)
                try:
                    self.balance.deposit(api, token, qty)
                except Exception:
                    raise ValueError("check_deposits: deposit failed")

            self.db.set(check_deposit_key, current_time)

    def withdraw_api(self, api_key, coinName, address, amount, *args, **kargs):
        self.balance.withdraw(user=api_key, token=coinName, amount=amount)
        token = utils.get_token(coinName)
        tx = web3_interface.withdraw(self.bank_address,
                                     token.address,
                                     int(amount * token.decimals),
                                     address)
        return {
            'tId': tx,
            'amountSent': amount,
            'funds': self.balance.get(user=api_key)
        }


def get_order_id(pair, rate, quantity):
    """Create Id for an order by hashing a string contain
    pair, it's rate and quantity
    """
    keys = [pair, rate, quantity]
    return hash('.'.join(map(str, keys))) % MAX_ORDER_ID
