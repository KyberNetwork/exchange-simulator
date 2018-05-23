from flask import Flask, request, jsonify

from simulator import utils, kraken

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/0/public/Ticker', methods=['GET'])
def ticker():
    """
        https://api.kraken.com/0/public/Ticker?pair=ETHUSD
        {
          "error": [],
          "result": {
            "XETHZUSD": {
              "a": [
                "692.44000",
                "7",
                "7.000"
              ],
              "b": [
                "691.56000",
                "9",
                "9.000"
              ],
              "c": [
                "691.85000",
                "2.39616613"
              ],
              "v": [
                "7639.93596626",
                "22921.84640364"
              ],
              "p": [
                "687.59350",
                "697.54052"
              ],
              "t": [
                2480,
                8360
              ],
              "l": [
                "680.60000",
                "680.60000"
              ],
              "h": [
                "698.38000",
                "721.38000"
              ],
              "o": "697.19000"
            }
          }
        }
    """
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())
        result = kraken_ticker.load(timestamp)
        return jsonify({
            "error": [],
            "result": result
        })
    except ValueError as e:
        logger.error(str(e))
        return jsonify({
            "error": [str(e)]
        })


rdb = utils.get_redis_db()
kraken_ticker = kraken.DataTicker(rdb)


if __name__ == '__main__':
    logger.debug(f"Running in {config.MODE} mode")
    api.run(host='0.0.0.0', port=5400, debug=True)
