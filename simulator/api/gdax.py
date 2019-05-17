from flask import Flask, request, jsonify

from simulator import utils, gdax

api = Flask(__name__)

logger = utils.get_logger()

# gdax = pro.coinbase
# https://api.pro.coinbase.com/products/eth-btc/ticker
# https://api.gdax.com/products/eth-usd/ticker
# {
#   "trade_id": 34555486,
#   "price": "693.77000000",
#   "size": "1.54000000",
#   "bid": "693.77",
#   "ask": "693.78",
#   "volume": "55144.81750776",
#   "time": "2018-05-22T06:59:00.989000Z"
# }


@api.route('/products/<base>-<quote>/ticker', methods=['GET'])
def ticker(base, quote):
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())
        result = data_ticker.load(timestamp, base, quote)
        return jsonify(result)
    except ValueError as e:
        logger.error(str(e))
        return jsonify({
            'message': str(e)
        })


rdb = utils.get_redis_db()
data_ticker = gdax.DataTicker(rdb)


if __name__ == '__main__':
    logger.debug(f"Running in {config.MODE} mode")
    api.run(host='0.0.0.0', port=5600, debug=True)
