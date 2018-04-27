from flask import Flask, request, jsonify

from simulator import utils, forge

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/1.0.3/convert', methods=['GET'])
def tick():
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())
        xau_eth_rate = forge_feeder.load(timestamp)
        return jsonify({
            'value': xau_eth_rate,
            'text': f"1 XAU is worth {xau_eth_rate} ETH",
            "timestamp": timestamp
        })
    except ValueError as e:
        logger.error(str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        })


rdb = utils.get_redis_db()
forge_feeder = forge.Feeder(rdb)


if __name__ == '__main__':
    logger.debug(f"Running in {config.MODE} mode")
    api.run(host='0.0.0.0', port=5500, debug=True)
