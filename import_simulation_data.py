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
    initialized_balances = rdb.get('INITIALIZED_BALANCES')
    if not initialized_balances:
        for ex, balance in config.INITIAL_BALANCE.items():
            key = config.API_KEY[ex]
            for token, amount in balance.items():
                balance_handler.deposit(key, token, amount, 'available')
        rdb.set('INITIALIZED_BALANCES', True)


if __name__ == '__main__':
    main()
