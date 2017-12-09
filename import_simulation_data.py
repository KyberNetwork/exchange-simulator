from simulator import utils, config
from simulator.balance_handler import BalanceHandler


def main():
    rdb = utils.get_redis_db()
    supported_tokens = config.SUPPORTED_TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    if config.MODE == 'simulation':
        rdb = utils.get_redis_db()
        ob_file = 'data/full_ob.dat'
        # ob_file = 'data/sample_ob.dat'
        utils.setup_data(rdb, ob_file)

    # init deposit
    initialized_balance = rdb.get('INITIALIZED_BINANCE_BALANCE')
    if not initialized_balance:
        user = config.DEFAULT_BINANCE_API_KEY
        balance_handler.deposit(user, 'omg', 50, 'available')
        balance_handler.deposit(user, 'eth', 1, 'available')
        # utils.init_deposit(balance=balance_handler,
        #                    user=user,
        #                    amount=100000, tokens=supported_tokens)
        rdb.set('INITIALIZED_BINANCE_BALANCE', True)

    # init deposit
    initialized_balance = rdb.get('INITIALIZED_LIQUI_BALANCE')
    if not initialized_balance:
        utils.init_deposit(balance=balance_handler,
                           user=config.DEFAULT_LIQUI_API_KEY,
                           amount=100000, tokens=supported_tokens)
        rdb.set('INITIALIZED_LIQUI_BALANCE', True)


if __name__ == '__main__':
    main()
