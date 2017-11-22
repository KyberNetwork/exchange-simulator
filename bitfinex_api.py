from flask import Flask

from simulator import config, utils
from simulator.exchange import Bitfinex

api = Flask(__name__)


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


def action(expected_params=[]):
    def decorator(func):
        @wraps(func)
        def wrapper():
            error = validate_params(expected_params)
            if error:
                return str(error)

            params = request.args.to_dict()

            api_key = request.headers.get('X-BFX-APIKEY')
            if not api_key:
                return str(MISSING_ERROR['api_key'])
            params['api_key'] = api_key.lower()

            params['timestamp'] = utils.get_timestamp(request.args.to_dict())

            logger.info('Params: {}'.format(params))
            result = func(params)
            logger.info('Output: {}'.format(result))

            return jsonify(result)
        return wrapper
    return decorator


@api.route('/book/<symbol>')
def order_book(symbol):
    timestamp = utils.get_timestamp(request.args.to_dict())
    return bitfinex.order_book_api(symbol, timestamp)


@api.route('/balances')
@action()
def balances(params):
    return bitfinex.balances_api(**params)


@api.route('/order/new')
@action()
def new_order(params):
    return bitfinex.trade_api(**params)


@api.route('/withdraw')
@action()
def withdraw(params):
    return bitfinex.withdraw_api(**params)


def main():
    api.run(port=5003, debug=True)


if __name__ == '__main__':
    rdb = utils.get_redis_db()
    if config.MODE == 'simulation':
        utils.setup_data(rdb)
        order_handler = SimulationOrder(rdb)
    else:
        order_handler = CoreOrder()
    supported_tokens = config.SUPPORTED_TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    bitfinex = Bitfinex(
        "bitfinex",
        list(supported_tokens.values()),
        rdb,
        order_handler,
        balance_handler,
        config.BITTREX_ADDRESS,
        config.DEPOSIT_DELAY
    )
    main()
