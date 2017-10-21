import datetime
import random
import time
import lwp

class Pairs:
    """A class that converts all exchange pairs to common pairs and the
    oposite"""

    def __init__(self):
        self.pairs = {
        'common': ['OMG-ETH', 'DGD-ETH', 'CVC-ETH', 'FUN-ETH', 'MCO-ETH',
                   'GNT-ETH', 'ADX-ETH', 'PAY-ETH', 'BAT-ETH', 'KNC-ETH',
                   'EOS-ETH', 'LINK-ETH'],
        'bittrex': ['ETH-OMG', 'ETH-DGD', 'ETH-CVC', 'ETH-FUN', 'ETH-MCO',
                    'ETH-GNT', 'ETH-ADX', 'ETH-PAY', 'ETH-BAT'],
        'liqui': ['omg_eth', 'dgd_eth', 'cvc_eth', 'mco_eth', 'gnt_eth',
                  'adx_eth', 'pay_eth', 'bat_eth', 'knc_eth', 'eos_eth'],
        'bitfinex': ['omgeth', 'eoseth'],
        'binance': ['OMGETH', 'FUNETH', 'MCOETH', 'KNCETH', 'EOSETH',
                    'LINKETH']}


    def ctoex(self, pair, exchange):
        """Common pair to exchange pair
        :param pair: any pair in 'common'
        :param exchange: any key in self.pairs except 'common' """
        def finddash(commonpair):
            """Get the first part of the common pair"""
            position = commonpair.index('-')
            return commonpair[:position]
        if pair.upper() in self.pairs['common']:
            basecur = finddash(pair.upper())
            for i in self.pairs[exchange]:
                if i.upper().startswith(basecur) or (
                        i.upper().endswith(basecur)  ):
                    return i

        else:
            raise ValueError('Pair is not traded at KN')

a1 = Pairs()
a1.ctoex('OMG-ETH', 'bittrex')
a1.ctoex('OMG-ETH', 'liqui')
a1.ctoex('OMG-ETH', 'binance')
a1.ctoex('LINK-ETH', 'binance')



    def extoc(self, pair, exchange):
        """Exchange pair to common pair
        :param pair: any pair in format of exchanges
        :param exchange: any key in self.pairs except 'common' """
        def finddash(commonpair):
            """Get the first part of the common pair"""
            position = commonpair.index('-')
            return commonpair[:position]
        if pair.upper() in self.pairs['common']:
            basecur = finddash(pair.upper())
            for i in self.pairs[exchange]:
                if i.upper().startswith(basecur) or (
                        i.upper().endswith(basecur)  ):
                    return i





        }
class Balance:
    """A class that keeps track and modifies a currency and it's balance """

    def __init__(self, curr):
        self.balance = {}
        self.balance[curr] = 0

    def change_balance(self, balance, curr):
        if self.balance[curr] + balance >= 0:
            self.balance[curr] = round((self.balance[curr] + balance), 8)
        else:
            raise ValueError('Negative Balance')

    def add_curr(self, curr):
        """

        :param curr:
        """
        if curr not in self.balance.keys():
            self.balance[curr] = 0


class Orders:
    """A class that keeps track of the Open orders for all exchanges and
    modifies those for quantity filled, cancels, etc"""

    def __init__(self):
        self.orders = {
            'bittrex': [],
            'liqui': [],
            'binance': [],
            'poloniex': [],
            'bitfinex': []
        }
        self.book = {
            'bittrex': {},
            'liqui': {},
            'binance': {},
            'poloniex': {},
            'bitfinex': {}

        }

    def new(self, exchange, market, side, quantity, rate):
        """Creates a new order object with the exchange parameters that will
        be used
        :param market:  is the KNname column of the symbols sheet in the
        'Data Fetcher' spreadsheet
        :param exchange: is the exchange name
        :param side: is  'BUY' or 'SELL'
        :param quantity: is the quantity desired to buy
        :param rate is the price
        """

        """Orderbook[market]['BUY'] needs to be sorted from high to low
        and orderbook[market][SELL] needs to be sorted low to high"""
        if side.upper() == 'BUY':
            rsort = True
        elif side.upper() == 'SELL':
            rsort = False

        if exchange.lower() == 'bittrex':
            order = {}
            x = '%0x' % random.getrandbits(32 * 4)
            order['OrderUuid'] = (
                x[:8] + '-' + x[8:12] + '-' + x[12:16] + '-' + x[16:32])
            order['Exchange'] = market.upper()
            order['OrderType'] = 'LIMIT_' + side.upper()
            order['Quantity'], order['QuantityRemaining'] = quantity, quantity
            order['Limit'] = rate
            order['CommissionPaid'] = 0
            order['Price'] = 0
            order['Opened'] = datetime.datetime.utcnow().isoformat(
                timespec='milliseconds')
            order['KNinternal1'] = side.upper()
            order['KNinternal2'] = market.upper()
            order['KNinternal3'] = order['OrderUuid']
            self.orders['bittrex'].append(order)

        elif exchange.lower() == 'liqui':
            order = {}
            orderid = str(int(time.time()*10))[1:]
            order['pair'] = market.upper()
            order['OrderType'] = 'LIMIT_' + side.upper()
            order['Quantity'], order['QuantityRemaining'] = quantity, quantity
            order['Limit'] = rate
            order['CommissionPaid'] = 0
            order['Price'] = 0
            order['Opened'] = datetime.datetime.utcnow().isoformat(
                timespec='milliseconds')
            order['KNinternal1'] = side.upper()
            order['KNinternal2'] = market.upper()
            order['KNinternal3'] = order['OrderUuid']
            self.orders['bittrex'].append(order)

        """Update the orderbook with the order price and orderID"""
        kn1 = order['KNinternal1']
        kn2 = order['KNinternal2']
        kn3 = order['KNinternal3']
        if kn2 not in self.book[exchange].keys():
            self.book[exchange][kn2] = {}
            self.book[exchange][kn2][kn1] = []
            self.book[exchange][kn2][kn1].append((rate, kn3))
            self.book[exchange][kn2][kn1].sort(reverse=rsort)
        elif kn1 not in (
            self.book[exchange][kn2].keys()):
            self.book[exchange][kn2][kn1] = []
            self.book[exchange][kn2][kn1].append((rate, kn3))
            self.book[exchange][kn2][kn1].sort(reverse=rsort)
        else:
            self.book[exchange][kn2][kn1].append((rate, kn3))
            self.book[exchange][kn2][kn1].sort(reverse=rsort)

    def cancel(self, exchange, orderid):
        """Given the orderid, remove the order from the orderbook and also
        remove it from the active orders list"""

        if len(self.orders[exchange]) >= 1:
            for e, order in enumerate(self.orders[exchange]):
                if orderid in order.values():
                    self.orders[exchange].pop(e)
                    for o in (
                            self.book[exchange][order['KNinternal2']]
                                [order['KNinternal1']]):
                        if o[1] == orderid:
                            (self.book[exchange][order['KNinternal2']]
                                 [order['KNinternal1']]).remove(o)
        else:
            raise KeyError("No orders to cancel from")

class Trader():
    """"Polls periodically (10s) API for lw prices and if there is a price
    that would cause the an order to execute, it fills that order """


def current_timestamp():
    """
    Return current timestamp
    """
    return int(round(time.time() * 1000))


lwp.get_knlw_prices(
[{'BaseToken': 'OMG', 'DestToken': 'ETH', 'PriceType': lwp.PriceType.ask,
  'RequiredQty': 1000, 'DateTimeStamp': 1508282098742}]
)

def convertmktex(cmark,emark)
def conver
def find_ex(url):
    """Returns the exchange that should handle the request given the url
    provided as param"""

    if url.lower().startswith('https://bittrex.com/api/'):
        return 'bittrex'
    elif url.lower().startswith('https://poloniex.com/tradingapi'):
        return 'poloniex'
    elif url.lower().startswith('https://api.liqui.io'):
        return 'bitfinex'
    elif url.lower().startswith('https://www.binance.com/api'):
        return 'binance'
    elif url.lower().startswith('https://api.bitfinex.com'):
        return 'bitfinex'
    else:
        raise Exception("Unknown Exchange in request URL")

#b=lwp.get_market_data(lwp.HOST)

a=Orders()
a.new('bittrex','omt-eth','buy',100,1.211)
a.new('bittrex','omt-eth','buy',100,1.311)
a.new('bittrex','omt-eth','sell',100,1.211)
a.new('bittrex','omt-eth','sell',100,1.251)
a.new('bittrex','omt-eth','sell',100,1.311)
