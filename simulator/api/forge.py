from flask import Flask, request, jsonify

from simulator import utils, forge

api = Flask(__name__)

logger = utils.get_logger()


@api.route('/1.0.3/convert', methods=['GET'])
def tick():
    try:
        timestamp = utils.get_timestamp(request.args.to_dict())

        base = request.args.get('from', 'XAU').upper()
        quote = request.args.get('to', 'USD').upper()
        amount = float(request.args.get('quantity', '1'))

        rate = forge_feeder.load(timestamp, base, quote, amount)
        worth = rate * amount
        return jsonify({
            'value': worth,
            'text': f"{amount} {base} is worth {worth} {quote}",
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
