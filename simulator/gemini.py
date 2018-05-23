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

            Using digix data
            TODO later we will use gemini data
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
            "bid": "0",
            "ask": "0",
            "volume": {
                "ETH": "0",
                "USD": "0",
                "timestamp": timestamp
            },
            "last": str(eth_usd_rate)
        }
