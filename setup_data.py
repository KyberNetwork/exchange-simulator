import argparse

from simulator import utils, config
from simulator.balance_handler import BalanceHandler


logger = utils.get_logger()


def import_captured_data():
    rdb = utils.get_redis_db()
    
    # rdb.flushall()
    # ob_path = 'data/order_books/'
    # utils.import_order_book_to_db(rdb, ob_path)

    rate_path = 'data/rates'
    utils.import_rates_to_db(rdb, rate_path)


def init_balance():
    rdb = utils.get_redis_db()
    supported_tokens = config.TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    # reset balance
    rdb.delete('INITIALIZED_BALANCES')
    for k in rdb.keys('balance*available'):
        rdb.delete(k)

    # init deposit
    initialized_balances = rdb.get('INITIALIZED_BALANCES')
    if not initialized_balances:
        for ex, balance in config.INITIAL_BALANCE.items():
            key = config.API_KEY[ex]
            for token, amount in balance.items():
                balance_handler.deposit(key, token, amount, 'available')
        rdb.set('INITIALIZED_BALANCES', True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup data for simulation.')
    parser.add_argument('-i', '--import-data', action='store_true',
                        help='import captured data into redis')
    args = parser.parse_args()
    if args.import_data:
        logger.info('Import captured data ...')
        import_captured_data()
    else:
        logger.info('Initialze balance for user/default_api on exchanges ...')
        init_balance()
    logger.info('Done')
