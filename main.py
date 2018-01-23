from multiprocessing import Process

from simulator.api import binance_api, bittrex_api, huobi_api
from simulator import utils, config

logger = utils.get_logger()


def run_api(api, port):
    logger.info(port)
    api.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    logger.info('Running in {} mode'.format(config.MODE))

    run_api(huobi_api, 5200)

    '''
    p1 = Process(target=run_api, args=(binance_api, 6100))
    p1.start()
    # p1.join()

    p2 = Process(target=run_api, args=(bittrex_api, 6300))
    p2.start()
    # p2.join()

    p3 = Process(target=run_api, args=(huobi_api, 6200))
    p3.start()
    # p3.join()

    p1.join()
    p2.join()
    p3.join()
    '''
