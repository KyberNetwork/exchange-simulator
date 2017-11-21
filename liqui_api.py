#!/usr/bin/python3
import time
import traceback

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import json
import redis
from raven.contrib.flask import Sentry


from simulator import config, utils
from simulator.exchange import Liqui
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler


logger = utils.get_logger()

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    try:
        api_key = request.headers.get('Key', None)
        if not api_key:
            raise AttributeError("Missing 'Key' Header")

        params = request.form.to_dict()
        params['api_key'] = api_key.lower()

        method = params.get('method', None)
        if not method:
            raise KeyError('Method is missing in your request')

        params['timestamp'] = request.args.get('timestamp',
                                               utils.get_current_timestamp())

        logger.info('Params: {}'.format(params))
        liqui.check_deposits(api_key)
        if method == 'getInfo':
            output = liqui.get_balance_api(**params)
        elif method == 'Trade':
            output = liqui.trade_api(**params)
        elif method == 'WithdrawCoin':
            output = liqui.withdraw_api(**params)
        elif method == 'OrderInfo':
            output = liqui.get_order_api(**params)
        else:
            raise AttributeError('Invalid method requested')
        logger.info('Output: {}'.format(output))
        return jsonify({
            'success': 1,
            'return': output
        })
    except Exception as e:
        # traceback.print_exc()
        return jsonify({
            'success': 0,
            'error': str(e)
        })


@app.route("/depth/<string:pairs>", methods=['GET'])
def depth(pairs):
    timestamp = request.args.get('timestamp', utils.get_current_timestamp())

    try:
        depth = liqui.get_depth_api(pairs, timestamp)
        return json.dumps(depth)
    except ValueError as e:
        logger.info("Bad Request: {}".format(e))
        return BadRequest()


rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()
supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())

# init deposit
initialized_balance = rdb.get('INITIALIZED_LIQUI_BALANCE')
if not initialized_balance:
    utils.init_deposit(balance=balance_handler,
                       user=config.DEFAULT_LIQUI_API_KEY,
                       amount=100000, tokens=supported_tokens)
    rdb.set('INITIALIZED_LIQUI_BALANCE', True)

liqui = Liqui(
    "liqui",
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.LIQUI_ADDRESS,
    config.DEPOSIT_DELAY
)

if config.MODE != 'dev':
    sentry = Sentry(app, dsn='https://c2c05c37737d4c0a9e75fc4693005c2c:'
                    '17e24d6686d34465b8a97801e6e31ba4@sentry.io/241770')


if __name__ == "__main__":
    logger.info("Running in {} mode".format(config.MODE))
    app.run(host='0.0.0.0', port=5000, debug=True)
