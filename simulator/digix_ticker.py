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
        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)
        original_ts = self._shift_time(timestamp)
        key = f'digix_{original_ts}'

        logger.debug(f'Get rates with {key}')

        result = self.rdb.get(key)
        if not result:
            raise ValueError(f'Rates is not available at {timestamp}')
        rates = json.loads(result)
        return rates
