from functools import wraps
import traceback

from flask import Flask, request, jsonify

from simulator import config, utils
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler
from simulator.exchange import Binance

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
            logger.debug('Original params: {}'.format(params))
            if not public:
                api_key = request.headers.get('X-MBX-APIKEY')
                if not api_key:
                    return str(MISSING_ERROR['api_key'])
                else:
                    params['api_key'] = api_key.lower()
                try:
                    binance.check_deposits(api_key)
                except Exception:
                    logger.error('Check deposit fail.')

            params['timestamp'] = utils.get_timestamp(request.args.to_dict())

            logger.debug('Params: {}'.format(params))
            try:
                result = func(params)
            except Exception as e:
                # traceback.print_exc()
                logger.info('Error Output: {}'.format(str(e)))
                return jsonify({'code': -1, 'msg': str(e)})

            logger.debug('Output: {}'.format(result))

            return jsonify(result)
        return wrapper
    return decorator


@api.route('/api/v1/depth', methods=['GET'])
@action(expected_params=['symbol'], public=True)
def order_book(params):
    return binance.get_order_book_api(**params)


@api.route('/api/v3/account', methods=['GET'])
@action(public=False)
def account(params):
    return binance.get_account_api(**params)


@api.route('/api/v3/order', methods=['POST'])
@action(public=False)
def create_order(params):
    return binance.trade_api(**params)


@api.route('/api/v3/order', methods=['GET'])
@action(public=False)
def get_order(params):
    return binance.get_order_api(**params)


@api.route('/api/v3/allOrders', methods=['GET'])
@action(public=False)
def get_all_orders(params):
    return binance.get_all_orders_api(**params)


@api.route('/api/v3/order', methods=['DELETE'])
@action(public=False)
def cancel_order(params):
    return binance.cancel_order_api(**params)


@api.route('/wapi/v3/withdraw.html', methods=['POST'])
@action(public=False)
def withdraw(params):
    return binance.withdraw_api(**params)


logger.info("Running in {} mode".format(config.MODE))

rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()

supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())

# init deposit
initialized_balance = rdb.get('INITIALIZED_BINANCE_BALANCE')
if not initialized_balance:
    utils.init_deposit(balance=balance_handler,
                       user=config.DEFAULT_BINANCE_API_KEY,
                       amount=100000, tokens=supported_tokens)
    rdb.set('INITIALIZED_BINANCE_BALANCE', True)

binance = Binance(
    "binance",
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.BINANCE_ADDRESS,
    config.DEPOSIT_DELAY
)

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=5100, debug=True)
