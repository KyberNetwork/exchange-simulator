from flask import Flask, request, jsonify

from simulator import utils, digix_ticker

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/tick', methods=['GET'])
def tick():
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())
        rates = data_ticker.load(timestamp)
        return jsonify({
            'success': True,
            'data': rates
        })
    except ValueError as e:
        logger.error(str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        })


rdb = utils.get_redis_db()
data_ticker = digix_ticker.DataTicker(rdb)


if __name__ == '__main__':
    logger.debug(f"Running in {config.MODE} model")
    api.run(host='0.0.0.0', port=5678, debug=True)
