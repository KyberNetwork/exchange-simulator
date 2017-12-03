from functools import wraps
import traceback

from flask import Flask, request, jsonify

from simulator import config, utils
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler
from simulator.exchange import Bittrex

api = Flask(__name__)

logger = utils.get_logger()


MISSING_ERROR = {
    'apikey': 'APISIGN_NOT_PROVIDED',
    'type': 'TYPE_NOT_PROVIDED',
    'market': 'MARKET_NOT_PROVIDED',
    'nonce': 'NONCE_NOT_PROVIDED'
}


def validate_params(expected_params):
    # logger.info('expect: {}'.format(expected_params))
    for p in expected_params:
        if not request.args.get(p):
            raise ValueError(MISSING_ERROR[p])


def action(expected_params):
    def decorator(func):
        @wraps(func)
        def wrapper():
            try:
                validate_params(expected_params)

                params = request.args.to_dict()
                params['timestamp'] = utils.get_timestamp(
                    request.args.to_dict())

                logger.debug('Params: {}'.format(params))
                result = func(params)
                logger.debug('Output: {}'.format(result))

                return jsonify({
                    'success': True,
                    'message': '',
                    'result': result
                })
            except Exception as e:
                # traceback.print_exc()
                logger.error(e)
                return jsonify({
                    'success': False,
                    'message': str(e),
                    'result': None
                })
        return wrapper
    return decorator


@api.route('/getorderbook')
@action(expected_params=['type', 'market'])
def get_order_book(params):
    return bittrex.get_order_book_api(**params)


@api.route('/account/getbalances')
@action(expected_params=['apikey', 'nonce'])
def get_balances(params):
    return bittrex.get_balance_api(**params)


@api.route('/market/buylimit')
@action(expected_params=['apikey', 'nonce'])
def buy_limit(params):
    params['type'] = 'buy'
    return bittrex.trade_api(**params)


@api.route('/market/selllimit')
@action(expected_params=['apikey', 'nonce'])
def sell_limit(params):
    params['type'] = 'sell'
    return bittrex.trade_api(**params)


@api.route('/market/getopenorders')
@action(expected_params=['apikey', 'nonce'])
def get_open_orders(params):
    return bittrex.get_open_orders_api(**params)


@api.route('/getorder')
@action(expected_params=['apikey', 'nonce'])
def get_order(params):
    return bittrex.get_order_api(**params)


@api.route('/market/cancel')
@action(expected_params=['apikey', 'nonce'])
def cancel_order(params):
    return bittrex.cancel_order_api(**params)


@api.route('/account/withdraw')
@action(expected_params=['apikey', 'nonce'])
def withdraw(params):
    return bittrex.withdraw_api(**params)


@api.route('/account/getdeposithistory')
@action(expected_params=['apikey', 'nonce'])
def deposit_history(params):
    return bittrex.deposit_history_api(**params)


@api.route('/account/getwithdrawalhistory')
@action(expected_params=['apikey', 'nonce'])
def withdrawal_history(params):
    return bittrex.withdrawal_history_api(**params)


rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()
supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())
bittrex = Bittrex(
    "bittrex",
    config.PRIVATE_KEY['bittrex'],
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.BITTREX_ADDRESS
)

if __name__ == '__main__':
    logger.info('Running in {} mode'.format(config.MODE))
    api.run(host='0.0.0.0', port=5300, debug=True)
