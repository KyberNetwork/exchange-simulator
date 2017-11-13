#!/usr/bin/python3
import os
import sys
import logging
import logging.config
import time
import traceback

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import json
import redis
from raven.contrib.flask import Sentry


from exchange import Exchange
from order_handler import CoreOrder, SimulationOrder
from balance_handler import BalanceHandler
import constants
import utils


logger = utils.get_logger()

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    try:
        if 'Key' not in request.headers:
            raise AttributeError("Missing 'Key' Header")
        else:
            api_key = request.headers['Key'].lower()

        timestamp = request.args.get('timestamp')
        if timestamp:
            timestamp = int(timestamp)
        else:
            timestamp = int(time.time() * 1000)

        params = request.form.to_dict()
        params['api_key'] = api_key
        params['timestamp'] = timestamp
        try:
            method = params['method']
        except KeyError:
            raise KeyError('Method is missing in your request')

        logger.info('Params: {}'.format(params))

        if method == 'getInfo':
            output = liqui_exchange.get_balance_api(**params)
        elif method == 'Trade':
            output = liqui_exchange.trade_api(**params)
        elif method == 'WithdrawCoin':
            output = liqui_exchange.withdraw_api(**params)
        else:
            raise AttributeError('Invalid method requested')

        logger.info('Output: {}'.format(output))

        return jsonify({
            'success': 1,
            'return': output
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': 0,
            'error': str(e)
        })


@app.route("/depth/<string:pairs>", methods=['GET'])
def depth(pairs):
    timestamp = request.args.get('timestamp')
    if timestamp:
        timestamp = int(timestamp)
    else:
        timestamp = int(time.time() * 1000)

    try:
        depth = liqui_exchange.get_depth_api(pairs, timestamp)
        return json.dumps(depth)
    except ValueError as e:
        logger.info("Bad Request: {}".format(e))
        return BadRequest()


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logging.info("Running in {} mode".format(constants.MODE))
    rdb = utils.get_redis_db()

    if constants.MODE == 'simulation':
        # import simulation data
        data_imported = rdb.get('IMPORTED_SIMULATION_DATA')
        if not data_imported:
            logger.info('Import simulation data ...')
            ob_file = 'data/full_ob.dat'
            # ob_file = 'data/sample_ob.dat'
            try:
                utils.copy_order_books_to_db(ob_file, rdb)
            except FileNotFoundError:
                sys.exit('Data is missing.')
            rdb.set('IMPORTED_SIMULATION_DATA', True)
            logger.info('Finish setup process.')

        order_handler = SimulationOrder(rdb)
    else:
        order_handler = CoreOrder()

    supported_tokens = constants.SUPPORTED_TOKENS
    balance_handler = BalanceHandler(rdb, supported_tokens.keys())

    # init deposit
    initialized_balance = rdb.get('INITIALIZED_BALANCE')
    if not initialized_balance:
        utils.init_deposit(balance=balance_handler,
                           user=constants.DEFAULT_API_KEY,
                           amount=1000, tokens=supported_tokens)
        rdb.set('INITIALIZED_BALANCE', True)

    liqui_exchange = Exchange(
        "liqui",
        supported_tokens.values(),
        rdb,
        order_handler,
        balance_handler,
        constants.LIQUI_ADDRESS,
        constants.BANK_ADDRESS,
        constants.DEPOSIT_DELAY
    )

    if constants.MODE != 'dev':
        sentry = Sentry(app, dsn='https://c2c05c37737d4c0a9e75fc4693005c2c:'
                        '17e24d6686d34465b8a97801e6e31ba4@sentry.io/241770')

    app.run(host='0.0.0.0', port=5000, debug=True)
