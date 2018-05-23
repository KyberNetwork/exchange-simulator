import json

from . import utils

logger = utils.get_logger()


class DataTicker:
    # _START_SIMULATION_TIME = 1518215420000
    _START_SIMULATION_TIME = 1518215100000
    _START_REAL_TIME = 1524096460000

    def __init__(self, rdb):
        self.rdb = rdb

    def _shift_time(self, timestamp):
        return timestamp - self._START_SIMULATION_TIME + self._START_REAL_TIME

    def load(self, timestamp):
        """
            https://api.gdax.com/products/eth-usd/ticker

            {
              "trade_id": 34555486,
              "price": "693.77000000",
              "size": "1.54000000",
              "bid": "693.77",
              "ask": "693.78",
              "volume": "55144.81750776",
              "time": "2018-05-22T06:59:00.989000Z"
            }

            Using digix data to simulate gdax data
            TODO later we will use gdax data
        """

        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)
        original_ts = self._shift_time(timestamp)
        key = f'digix_{original_ts}'

        logger.debug(f'Get rates with {key}')

        result = self.rdb.get(key)
        if not result:
            raise ValueError(f'Rates is not available at {timestamp}')
        rates = json.loads(result)

        eth_usd_rate = 0
        for rate in rates:
            if rate['symbol'] == 'ETHUSD':
                eth_usd_rate = rate['price']

        return {
            'trade_id': 0,
            'price': str(eth_usd_rate),
            'size': '0',
            'bid': '0',
            'ask': '0',
            'volume': '0',
            'time': utils.fmt_time_from_timestamp(timestamp / 1000)
        }
