from uwsgidecorators import timer, harakiri, lock

from simulator import config
from simulator import utils
from simulator.balance_handler import BalanceHandler
from simulator.order_handler import CoreOrder, SimulationOrder
from simulator.exchange import Binance, Liqui

logger = utils.get_logger()

rdb = utils.get_redis_db()
if config.MODE == 'simulation':
    order_handler = SimulationOrder(rdb)
else:
    order_handler = CoreOrder()
supported_tokens = config.SUPPORTED_TOKENS
balance_handler = BalanceHandler(rdb, supported_tokens.keys())


liqui = Liqui(
    'liqui',
    config.PRIVATE_KEY['liqui'],
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.LIQUI_ADDRESS
)


binance = Binance(
    'binance',
    config.PRIVATE_KEY['binance'],
    list(supported_tokens.values()),
    rdb,
    order_handler,
    balance_handler,
    config.BINANCE_ADDRESS
)


exchanges = [
    [binance, config.DEFAULT_BINANCE_API_KEY],
    [liqui, config.DEFAULT_LIQUI_API_KEY]
]


@timer(config.DEPOSIT_DELAY)
@harakiri(10)
@lock
def update_balance(signum):
    for ex, api_key in exchanges:
        logger.info('Check deposit on {}'.format(ex.name))
        try:
            ex.check_deposits(api_key)
        except Exception as e:
            logger.error('Check deposit failed {}'.format(e))
