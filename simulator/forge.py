import json

from . import utils

logger = utils.get_logger()


class Feeder:
    # _START_SIMULATION_TIME = 1518215420000
    _START_SIMULATION_TIME = 1518215100000
    _START_REAL_TIME = 1524096460000

    def __init__(self, rdb):
        self.rdb = rdb

    def _shift_time(self, timestamp):
        return timestamp - self._START_SIMULATION_TIME + self._START_REAL_TIME

    def load(self, timestamp):
        """Using digix rates to interpret xau/eth from xau/usd and
        eth/usd
        TODO later we will capture forge data
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

        xau_eth_rate = 0
        xau_usd_rate = 0
        eth_usd_rate = 0

        for rate in rates:
            if rate['symbol'] == 'XAUUSD':
                xau_usd_rate = rate['price']
                continue
            if rate['symbol'] == 'ETHUSD':
                eth_usd_rate = rate['price']
                continue
            continue

        if eth_usd_rate > 0:
            xau_eth_rate = round(xau_usd_rate / eth_usd_rate, 5)

        return xau_eth_rate
