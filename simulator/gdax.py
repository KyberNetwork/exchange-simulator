import json

from . import utils

logger = utils.get_logger()


class DataTicker:

    def __init__(self, rdb):
        self.rdb = rdb

    def load(self, timestamp, base, quote):
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

            We are using binance orderbook
            TODO later we will use gdax data
        """
        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)

        if quote.lower() == 'usd':
            quote = 'usdt'        

        key = f'binance_{base}_{quote}_{timestamp}'.lower()
        logger.debug(f'Get rates with {key}')

        raw_order_book = self.rdb.get(key)
        if not raw_order_book:
            raise ValueError(f'Rates is not available at {timestamp}')
        
        order_book = json.loads(raw_order_book)
        ask_rate = order_book['Asks'][0]['Rate']
        bid_rate = order_book['Bids'][0]['Rate']
        rate = (ask_rate+bid_rate) / 2

        return {
            'trade_id': 0,
            'price': str(rate),
            'size': '0',
            'bid': str(bid_rate),
            'ask': str(ask_rate),
            'volume': '0',
            'time': utils.fmt_time_from_timestamp(timestamp / 1000)
        }
