from flask import Flask, request, jsonify

from simulator import utils, gemini

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/v1/pubticker/<symbol>', methods=['GET'])
def ticker(symbol):
    """
        https://api.gemini.com/v1/pubticker/ethusd
        {
          "bid": "692.09",
          "ask": "693.28",
          "volume": {
            "ETH": "20235.04104454",
            "USD": "13999965.86140211479999999999999999999704534",
            "timestamp": 1526975400000
          },
          "last": "693.77"
        }
    """
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())
        result = gemini_ticker.load(timestamp, symbol)
        return jsonify(result)
    except ValueError as e:
        logger.error(str(e))
        return jsonify({
            "result": "",
            "reason": "",
            "error": str(e)
        })


rdb = utils.get_redis_db()
gemini_ticker = gemini.DataTicker(rdb)


if __name__ == '__main__':
    logger.debug(f"Running in {config.MODE} mode")
    api.run(host='0.0.0.0', port=5800, debug=True)
