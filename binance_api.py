from functools import wraps

from flask import Flask, request, jsonify

from simulator import config, utils
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler
from simulator.exchange_binance import Binance

api = Flask(__name__)

logger = utils.get_logger()

MISSING_ERROR = {
    'symbol': {
        'code': -1102,
        'msg': "Mandatory parameter 'symbol' was not sent, "
        "was empty/null, or malformed."
    },
    'api_key': {
        'code': -2015,
        'msg': 'Invalid read-key, API-key, and/or IP.'
    }
}


def validate_params(expected_params):
    for p in expected_params:
        if not request.args.get(p):
            return MISSING_ERROR['symbol']


def action(expected_params=[], public=False):
    def decorator(func):
        @wraps(func)
        def wrapper():
            error = validate_params(expected_params)
            if error:
                return str(error)

            params = request.args.to_dict()
            if not public:
                api_key = request.headers.get('X-MBX-APIKEY')
                if not api_key:
                    return str(MISSING_ERROR['api_key'])
                else:
                    params['api_key'] = api_key.lower()

            timestamp = request.args.get('timestamp')
            if 'timestamp' not in params:
                params['timestamp'] = utils.get_current_timestamp()

            logger.info('Params: {}'.format(params))
            result = func(params)
            logger.info('Output: {}'.format(result))

            return jsonify(result)
        return wrapper
    return decorator


@api.route('/depth', methods=['GET'])
@action(expected_params=['symbol'], public=True)
def order_book(params):
    return binance.get_order_book_api(**params)


@api.route('/account', methods=['GET'])
@action(public=False)
def account(params):
    return binance.get_account_api(**params)


@api.route('/order', methods=['POST'])
@action(public=False)
def order(params):
    return binance.trades(**params)


@api.route('/withdraw.html', methods=['POST'])
@action(public=False)
def withdraw(params):
    return binance.withdraw_api(**params)


def main():
    api.run(debug=True)


if __name__ == '__main__':
    rdb = utils.get_redis_db()
    if config.MODE == 'simulation':
        utils.setup_data(rdb)
        order_handler = SimulationOrder(rdb)
    else:
        order_handler = CoreOrder()
    supported_tokens = config.SUPPORTED_TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    binance = Binance(
        "binance",
        list(supported_tokens.values()),
        rdb,
        order_handler,
        balance_handler,
        config.BINANCE_ADDRESS,
        config.BANK_ADDRESS,
        config.DEPOSIT_DELAY
    )
    main()