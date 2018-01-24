import traceback
from flask import Flask, jsonify, request

from simulator import config, utils
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler
from simulator.exchange import Huobi

api = Flask(__name__)

logger = utils.get_logger()


def err_to_json(e):
    return jsonify({
        'status': 'error',
        'err-code': '',
        'err-msg': str(e)
    })


def exec(f, additional_params={}):
    try:
        params = request.args.to_dict()
        params['api_key'] = params.get('AccessKeyId', None)
        if not params['api_key']:
            raise ValueError('Invalid access key id')
        params.update(additional_params)
        params['timestamp'] = utils.get_timestamp(request.args.to_dict())

        logger.info('Params: {}'.format(params))
        result = f(**params)
        logger.info('Result: {}'.format(result))
        return jsonify({
            'status': 'ok',
            'data': result
        })
    except Exception as e:
        # traceback.print_exc()
        return jsonify({
            'status': 'error',
            'err-code': '0',
            'err-msg': str(e)
        })


@api.route('/v1/common/symbols', methods=['GET'])
def exchange_info():
    return jsonify(huobi.get_info_api())


# GET /market/depth
@api.route('/market/depth', methods=['GET'])
def depth():
    timestamp = utils.get_timestamp(request.args.to_dict())
    params = request.args.to_dict()
    params['timestamp'] = timestamp
    try:
        result = huobi.get_depth_api(**params)
        return jsonify({
            'status': 'ok',
            'ts': timestamp,
            'tick': result
        })
    except Exception as e:
        return err_to_json(e)


# GET /v1/account/accounts # get list of
@api.route('/v1/account/accounts', methods=['GET'])
def accounts():
    return jsonify({
        'status': 'ok',
        'data': [
            {
                'id': 100009,
                'type': 'spot',
                'state': 'working',
                'user-id': 1000
            }
        ]
    })


# GET /v1/account/accounts/{account-id}/balance Get balance
@api.route('/v1/account/accounts/<account_id>/balance', methods=['GET'])
def balance(account_id):
    additional_params = {'account_id': account_id}
    return exec(huobi.get_balance_api, additional_params)


# POST /v1/order/orders/place Make an order
@api.route('/v1/order/orders/place', methods=['POST'])
def place_order():
    logger.info('hola')
    return exec(huobi.trade_api)


# POST /v1/order/orders/{order-id}/submitcancel
@api.route('/v1/order/orders/<order_id>/submitcancel', methods=['POST'])
def cancel_order(order_id):
    additional_params = {'order_id': order_id}
    return exec(huobi.cancel_order_api, additional_params)


# GET /v1/order/orders/{order-id} Get Order Info
@api.route('/v1/order/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    additional_params = {'order_id': order_id}
    return exec(huobi.get_order_api, additional_params)


# GET /v1/order/orders Get Order list
@api.route('/v1/order/orders', methods=['GET'])
def get_open_order():
    return exec(huobi.get_open_orders_api)


# POST /v1/dw/withdraw/api/create Create a withdraw application
@api.route('/v1/dw/withdraw/api/create', methods=['POST'])
def withdraw():
    return exec(huobi.withdraw_api)


@api.route('/v1/query/finances', methods=['GET'])
def history():
    return exec(huobi.history_api)


@api.route('/ping')
def ping():
    return 'pong'


rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()

supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())

huobi = Huobi(
    'binance',
    config.PRIVATE_KEY['huobi'],
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.EXCHANGES_ADDRESS['huobi'],
    config.EXCHANGE_INFO['huobi']
)

if __name__ == '__main__':
    logger.info("Running in {} mode".format(config.MODE))
    api.run(host='0.0.0.0', port=5200, debug=True)
