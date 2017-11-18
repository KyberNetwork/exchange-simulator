from functools import wraps

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
                timestamp = request.args.get('timestamp')
                if not timestamp:
                    timestamp = utils.get_current_timestamp()
                params['timestamp'] = timestamp

                logger.info('Params: {}'.format(params))
                result = func(params)
                logger.info('Output: {}'.format(result))

                return jsonify({
                    'success': True,
                    'message': '',
                    'result': result
                })
            except Exception as e:
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


@api.route('/account/withdraw')
@action(expected_params=['apikey', 'nonce'])
def withdraw(params):
    return bittrex.withdraw_api(**params)


def main():
    api.run(port=5001, debug=True)


if __name__ == '__main__':
    rdb = utils.get_redis_db()
    if config.MODE == 'simulation':
        utils.setup_data(rdb)
        order_handler = SimulationOrder(rdb)
    else:
        order_handler = CoreOrder()
    supported_tokens = config.SUPPORTED_TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    bittrex = Bittrex(
        "bittrex",
        list(supported_tokens.values()),
        rdb,
        order_handler,
        balance_handler,
        config.BITTREX_ADDRESS,
        config.DEPOSIT_DELAY
    )
    main()
