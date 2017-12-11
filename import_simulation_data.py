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
    default_api_keys = [
        config.DEFAULT_LIQUI_API_KEY,        
        config.DEFAULT_BITTREX_API_KEY,
        config.DEFAULT_BINANCE_API_KEY
    ]
    if not initialized_balances:
        # key = config.DEFAULT_BINANCE_API_KEY
        # balance_handler.deposit(key, 'omg', 50, 'available')
        # balance_handler.deposit(key, 'eth', 1, 'available')        

        for token in supported_tokens:
            for key in default_api_keys:
                balance_handler.deposit(key, token, 100000, 'available')
        rdb.set('INITIALIZED_BALANCES', True)



if __name__ == '__main__':
    main()
