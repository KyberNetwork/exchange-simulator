from functools import wraps

from flask import Flask, request, jsonify

from simulator import config, utils
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler
from simulator.exchange import Bitfinex

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


def action(expected_params=[]):
    def decorator(func):
        @wraps(func)
        def wrapper():
            error = validate_params(expected_params)
            if error:
                return str(error)

            params = request.form.to_dict()

            api_key = request.headers.get('X-BFX-APIKEY')
            if not api_key:
                return str(MISSING_ERROR['api_key'])
            params['api_key'] = api_key.lower()

            params['timestamp'] = utils.get_timestamp(request.args.to_dict())

            logger.info('Params: {}'.format(params))
            try:
                result = func(params)
                logger.info('Output: {}'.format(result))
                return jsonify(result)
            except Exception as e:
                logger.error(e)
                return jsonify({
                    'message': str(e)
                })
        return wrapper
    return decorator


@api.route('/v1/book/<symbol>', methods=['GET'])
def order_book(symbol):
    timestamp = utils.get_timestamp(request.args.to_dict())
    try:
        return jsonify(bitfinex.order_book_api(symbol, timestamp))
    except Exception as e:
        return jsonify({
            'message': str(e)
        })


@api.route('/v1/balances', methods=['POST'])
@action()
def balances(params):
    return bitfinex.balances_api(**params)


@api.route('/v1/order/new', methods=['POST'])
@action()
def new_order(params):
    return bitfinex.trade_api(**params)


@api.route('/v1/orders', methods=['POST'])
@action()
def active_orders(params):
    return bitfinex.active_orders_api(**params)


@api.route('/v1/order/status', methods=['POST'])
@action()
def order_status(params):
    return bitfinex.order_status_api(**params)


@api.route('/v1/order/cancel', methods=['POST'])
@action()
def cancel_order(params):
    return bitfinex.cancel_order_api(**params)


@api.route('/v1/withdraw', methods=['POST'])
@action()
def withdraw(params):
    return bitfinex.withdraw_api(**params)


@api.route('/v1/history/movements', methods=['POST'])
@action()
def history(params):
    return bitfinex.history_api(**params)


rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()
supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())
bitfinex = Bitfinex(
    'liqui',
    config.PRIVATE_KEY['bitfinex'],
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.BITFINEX_ADDRESS
)

if __name__ == '__main__':
    logger.info('Running in {} mode'.format(config.MODE))
    api.run(host='0.0.0.0', port=5400, debug=True)
