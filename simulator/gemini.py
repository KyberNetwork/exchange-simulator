import json

from . import utils

logger = utils.get_logger()


class DataTicker:

    def __init__(self, rdb):
        self.rdb = rdb

    def load(self, timestamp, symbol):
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

            We are using binance orderbook
            TODO later we will use gemini data
        """
        timestamp = int(timestamp)
        timestamp = utils.normalize_timestamp(timestamp)

        base, quote = self.__symbol_to_pair(symbol)

        if quote.lower() == 'usd':
            key = f'binance_{base}_usdt_{timestamp}'.lower()
        else:
            key = f'binance_{base}_{quote}_{timestamp}'.lower()            
        logger.debug(f'Get rates with {key}')

        raw_order_book = self.rdb.get(key)
        if not raw_order_book:
            raise ValueError(f'Rates is not available at {timestamp}')
        
        order_book = json.loads(raw_order_book)
        ask_rate = order_book['Asks'][0]['Rate']
        bid_rate = order_book['Bids'][0]['Rate']
        rate = (ask_rate + bid_rate) / 2

        return {
            "bid": str(bid_rate),
            "ask": str(ask_rate),
            "volume": {
                base.upper(): "0",
                quote.upper(): "0",
                "timestamp": timestamp
            },
            "last": str(rate)
        }

    def __symbol_to_pair(self, symbol):
        base, quote = symbol[:-3], symbol[-3:]
        return base, quote
