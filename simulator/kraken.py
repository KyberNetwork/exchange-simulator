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
            TODO: later we need to use kraken data
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
            "XETHZUSD": {
                "a": ["0", "0", "0"],
                "b": ["0", "0", "0"],
                "c": [str(eth_usd_rate), "0"],
                "v": ["0", "0"],
                "p": ["0", "0"],
                "t": [0, 0],
                "l": ["0", "0"],
                "h": ["0", "0"],
                "o": "0"
            }
        }
