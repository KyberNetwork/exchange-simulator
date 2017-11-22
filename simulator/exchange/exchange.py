#!/usr/bin/python3
import time

from .. import web3_interface, utils
from ..order import Order


logger = utils.get_logger()


class Exchange:

    def __init__(self, exchange_name, supported_tokens, db,
                 order_handler, balance_handler,
                 deposit_address, deposit_delay_in_secs):
        self.name = exchange_name
        self.supported_tokens = supported_tokens
        self.db = db
        self.balance = balance_handler
        self.orders = order_handler
        self.deposit_address = deposit_address
        self.deposit_delay_in_secs = deposit_delay_in_secs
        self.processed_order_ids = set()

    def get_balance(self, api_key):
        return self.balance.get(user=api_key)

    def check_pair(self, pair):
        base, quote = pair.split('_')
        base_is_supported = any(base == t.token for t in self.supported_tokens)
        quote_is_ether = quote == 'eth'
        if (not base_is_supported) or (not quote_is_ether):
            raise ValueError('Invalid pair {}.'.format(pair))

    def get_order_book(self, pair, timestamp):
        self.check_pair(pair)
        try:
            order_book = self.orders.load(pair, self.name, timestamp)
        except Exception as e:
            logger.info('Order book {}_{} is missing'.format(pair, timestamp))
            order_book = {'Asks': [], 'Bids': []}

        # logger.debug("Order Book: {}".format(order_book))
        return order_book

    def trade(self, api_key, type, rate, pair, amount, timestamp):
        rate, amount = float(rate), float(amount)
        self.check_pair(pair)
        base, quote = pair.split('_')
        type = type.lower()

        # 1. lock balance
        if type == 'buy':
            self.balance.withdraw(api_key, quote, rate * amount)
        elif type == 'sell':
            self.balance.withdraw(api_key, base, amount)
        else:
            raise ValueError('Invalid type of order.')

        # 2. open new order
        new_order = Order(pair, type, rate, amount)

        # 3. match new order
        base_change, quote_change = self._match_order(api_key,
                                                      type,
                                                      rate,
                                                      pair,
                                                      amount,
                                                      timestamp)

        # 4. update balance and order
        # update order & balance
        # we are not holding balance for remaining order
        new_order.executed_amount = base_change
        new_order.remaining_amount = amount - base_change
        self.orders.add(new_order)
        if type == 'buy':
            self.balance.deposit(api_key, base, base_change)
            self.balance.deposit(api_key, quote, rate * amount - quote_change)
        else:
            self.balance.deposit(api_key, base, amount - base_change)
            self.balance.deposit(api_key, quote, quote_change)

        return {
            'received': new_order.executed_amount,
            'remaining': new_order.remaining_amount,
            'order_id': new_order.id
        }

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

            # id = get_order_id(pair, order['Rate'], order['Quantity'])
            # if id in self.processed_order_ids:
            # continue  # order is already processed, continue to next order

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

        return base_change, quote_change

    def get_order(self, order_id):
        return self.orders.get(order_id)

    def check_deposits(self, api_key):
        # check enough time passed since last deposit check
        check_deposit_key = ','.join([self.name, 'last_deposit_check'])
        last_check = self.db.get(check_deposit_key)

        if not last_check:
            last_check = 0
        else:
            last_check = int(last_check)

        current_time = utils.get_timestamp()
        if(current_time >= last_check + self.deposit_delay_in_secs * 1000):
            try:
                balances = web3_interface.get_balances(
                    self.deposit_address,
                    [token.address for token in self.supported_tokens])
            except Exception as e:
                logger.error(e)
                logger.info('Checking deposit fail.')
                return

            if(sum(balances) > 0):
                logger.info('Got some deposit.')
                try:
                    tx = web3_interface.clear_deposits(
                        self.deposit_address,
                        [token.address for token in self.supported_tokens],
                        balances)
                except Exception as e:
                    logger.error('Clear deposit fail.')
                    return

            for idx, balance in enumerate(balances):
                token = self.supported_tokens[idx]
                qty = float(balance) / (10**token.decimals)
                try:
                    self.balance.deposit(api_key, token.token, qty)
                except Exception as e:
                    logger.error(e)
                    raise ValueError("check_deposits: deposit failed")

            self.db.set(check_deposit_key, current_time)

    def withdraw(self, api_key, coinName, address, amount):
        coinName = coinName.lower()
        amount = float(amount)
        self.balance.withdraw(user=api_key, token=coinName, amount=amount)
        token = utils.get_token(coinName)
        tx = web3_interface.withdraw(self.deposit_address,
                                     token.address,
                                     int(amount * 10**token.decimals),
                                     address)
        return tx


MAX_ORDER_ID = 2 ** 31


def get_order_id(pair, rate, quantity):
    """Create Id for an order by hashing a string contain
    pair, it's rate and quantity
    """
    keys = [pair, rate, quantity]
    return hash('.'.join(map(str, keys))) % MAX_ORDER_ID
