import traceback

from flask import Flask, request, jsonify

from simulator import config, utils
from simulator.exchange import Poloniex
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.balance_handler import BalanceHandler

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/public')
def public():
    params = request.args.to_dict()
    command = params.get('command')
    if command == 'returnOrderBook':
        params['timestamp'] = utils.get_timestamp()
        try:
            ob = poloniex.order_book_api(**params)
            return jsonify(ob)
        except Exception as e:
            logger.error(e)
            return jsonify({
                'error': str(e)
            })
    else:
        return jsonify({
            'error': 'command {} is not supported'.format(command)
        })


@api.route('/tradingApi')
def trading_api():
    try:
        api_key = request.headers.get('Key')
        if not api_key:
            raise ValueError('Key is missing ')

        params = request.args.to_dict()
        params['api_key'] = api_key
        command = params.get('command')
        params['timestamp'] = utils.get_timestamp(request.args.to_dict())

        if command == 'returnBalances':
            output = poloniex.get_balance_api(**params)
        elif command == 'returnDepositsWithdrawals':
            output = poloniex.get_history_api(**params)
        elif command == 'returnOpenOrders':
            output = poloniex.get_open_orders_api(**params)
        elif command == 'sell' or command == 'buy':
            params['type'] = command
            output = poloniex.trade_api(**params)
        elif command == 'cancelOrder':
            output = poloniex.cancel_order_api(**params)
        elif command == 'withdraw':
            output = poloniex.withdraw_api(**params)
        else:
            return jsonify({
                'error': 'command {} is not supported'.format(command)
            })
        return jsonify(output)
    except Exception as e:
        # traceback.print_exc()
        logger.error(e)
        return jsonify({'error': str(e)})


rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()

balance_handler = BalanceHandler(rdb, config.TOKENS.keys())

poloniex = Poloniex(config.EXCHANGES_CFG['poloniex'],
                    order_handler,
                    balance_handler)


if __name__ == '__main__':
    logger.info('Running in {} mode'.format(config.MODE))
    api.run(host='0.0.0.0', port=5500, debug=True)
