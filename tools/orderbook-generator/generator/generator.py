import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import aioredis
import fire

from generator.orderbook import OrderBook, Ask, Bid, orderbook_to_json

Product = namedtuple("Product", ["name", "method"])

PRODUCTS = [
    Product(name="Initial", method="STANDARD")
]

# TODO: Move to some "config" module
OUTPUT_PATH_BASE = "output"


# 127.0.0.1:6379> get binance_trx_eth_1518228220000
# "{\"Asks\": [{\"Quantity\": 1837, \"Rate\": 6.129e-05}, {\"Quantity\": 90674, \"Rate\": 6.13e-05}, {\"Quantity\": 1132, \"Rate\": 6.132e-05}, {\"Quantity\": 943, \"Rate\": 6.135e-05}, {\"Quantity\": 6304, \"Rate\": 6.14e-05}, {\"Quantity\": 1275, \"Rate\": 6.145e-05}, {\"Quantity\": 5332, \"Rate\": 6.149e-05}, {\"Quantity\": 2400, \"Rate\": 6.15e-05}, {\"Quantity\": 64719, \"Rate\": 6.153e-05}, {\"Quantity\": 79810, \"Rate\": 6.154e-05}, {\"Quantity\": 19359, \"Rate\": 6.155e-05}, {\"Quantity\": 1033, \"Rate\": 6.156e-05}, {\"Quantity\": 3882, \"Rate\": 6.157e-05}, {\"Quantity\": 25871, \"Rate\": 6.159e-05}, {\"Quantity\": 4184839, \"Rate\": 6.16e-05}, {\"Quantity\": 47329, \"Rate\": 6.164e-05}, {\"Quantity\": 70905, \"Rate\": 6.17e-05}, {\"Quantity\": 449, \"Rate\": 6.172e-05}, {\"Quantity\": 162, \"Rate\": 6.173e-05}, {\"Quantity\": 10124, \"Rate\": 6.175e-05}, {\"Quantity\": 286, \"Rate\": 6.177e-05}, {\"Quantity\": 43285, \"Rate\": 6.18e-05}, {\"Quantity\": 369, \"Rate\": 6.182e-05}, {\"Quantity\": 6874, \"Rate\": 6.185e-05}, {\"Quantity\": 4082, \"Rate\": 6.187e-05}, {\"Quantity\": 14829, \"Rate\": 6.19e-05}, {\"Quantity\": 4175, \"Rate\": 6.193e-05}, {\"Quantity\": 23334, \"Rate\": 6.194e-05}, {\"Quantity\": 634, \"Rate\": 6.196e-05}, {\"Quantity\": 33325, \"Rate\": 6.198e-05}, {\"Quantity\": 48302, \"Rate\": 6.199e-05}, {\"Quantity\": 97796, \"Rate\": 6.2e-05}, {\"Quantity\": 44666, \"Rate\": 6.205e-05}, {\"Quantity\": 22958, \"Rate\": 6.206e-05}, {\"Quantity\": 3650, \"Rate\": 6.207e-05}, {\"Quantity\": 3760, \"Rate\": 6.209e-05}, {\"Quantity\": 41596, \"Rate\": 6.21e-05}, {\"Quantity\": 2365, \"Rate\": 6.212e-05}, {\"Quantity\": 27688, \"Rate\": 6.213e-05}, {\"Quantity\": 62071, \"Rate\": 6.214e-05}, {\"Quantity\": 23374, \"Rate\": 6.215e-05}, {\"Quantity\": 8260, \"Rate\": 6.219e-05}, {\"Quantity\": 18520, \"Rate\": 6.22e-05}, {\"Quantity\": 50887, \"Rate\": 6.225e-05}, {\"Quantity\": 600, \"Rate\": 6.227e-05}, {\"Quantity\": 211461, \"Rate\": 6.23e-05}, {\"Quantity\": 8950, \"Rate\": 6.231e-05}, {\"Quantity\": 2097, \"Rate\": 6.233e-05}, {\"Quantity\": 4071, \"Rate\": 6.235e-05}, {\"Quantity\": 403, \"Rate\": 6.24e-05}], \"Bids\": [{\"Quantity\": 46509, \"Rate\": 6.121e-05}, {\"Quantity\": 2800, \"Rate\": 6.114e-05}, {\"Quantity\": 70000, \"Rate\": 6.113e-05}, {\"Quantity\": 3000, \"Rate\": 6.112e-05}, {\"Quantity\": 334, \"Rate\": 6.108e-05}, {\"Quantity\": 40000, \"Rate\": 6.107e-05}, {\"Quantity\": 57673, \"Rate\": 6.105e-05}, {\"Quantity\": 2002, \"Rate\": 6.104e-05}, {\"Quantity\": 121980, \"Rate\": 6.101e-05}, {\"Quantity\": 167327, \"Rate\": 6.1e-05}, {\"Quantity\": 281, \"Rate\": 6.099e-05}, {\"Quantity\": 256, \"Rate\": 6.098e-05}, {\"Quantity\": 174670, \"Rate\": 6.09e-05}, {\"Quantity\": 5572, \"Rate\": 6.084e-05}, {\"Quantity\": 6773, \"Rate\": 6.083e-05}, {\"Quantity\": 17125, \"Rate\": 6.08e-05}, {\"Quantity\": 4771, \"Rate\": 6.078e-05}, {\"Quantity\": 197, \"Rate\": 6.077e-05}, {\"Quantity\": 65556, \"Rate\": 6.076e-05}, {\"Quantity\": 65865, \"Rate\": 6.073e-05}, {\"Quantity\": 53008, \"Rate\": 6.07e-05}, {\"Quantity\": 1648, \"Rate\": 6.068e-05}, {\"Quantity\": 45356, \"Rate\": 6.065e-05}, {\"Quantity\": 518, \"Rate\": 6.064e-05}, {\"Quantity\": 62540, \"Rate\": 6.06e-05}, {\"Quantity\": 6000, \"Rate\": 6.059e-05}, {\"Quantity\": 3902, \"Rate\": 6.055e-05}, {\"Quantity\": 5672, \"Rate\": 6.053e-05}, {\"Quantity\": 415, \"Rate\": 6.051e-05}, {\"Quantity\": 71118, \"Rate\": 6.05e-05}, {\"Quantity\": 10501, \"Rate\": 6.047e-05}, {\"Quantity\": 2407, \"Rate\": 6.045e-05}, {\"Quantity\": 779, \"Rate\": 6.044e-05}, {\"Quantity\": 320, \"Rate\": 6.043e-05}, {\"Quantity\": 613, \"Rate\": 6.041e-05}, {\"Quantity\": 11789, \"Rate\": 6.04e-05}, {\"Quantity\": 319, \"Rate\": 6.035e-05}, {\"Quantity\": 2800, \"Rate\": 6.033e-05}, {\"Quantity\": 1895, \"Rate\": 6.032e-05}, {\"Quantity\": 1375, \"Rate\": 6.03e-05}, {\"Quantity\": 56497, \"Rate\": 6.027e-05}, {\"Quantity\": 3741, \"Rate\": 6.025e-05}, {\"Quantity\": 365, \"Rate\": 6.024e-05}, {\"Quantity\": 1333, \"Rate\": 6.022e-05}, {\"Quantity\": 61940, \"Rate\": 6.021e-05}, {\"Quantity\": 5112, \"Rate\": 6.02e-05}, {\"Quantity\": 648, \"Rate\": 6.019e-05}, {\"Quantity\": 140091, \"Rate\": 6.015e-05}, {\"Quantity\": 336, \"Rate\": 6.014e-05}, {\"Quantity\": 2800, \"Rate\": 6.011e-05}]}"

def prepare_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def prepare_output_path(output_dir):
    output = Path(output_dir) / prepare_current_timestamp()
    output.mkdir(parents=True)
    log.info(f"Preparing output path: {output.absolute()}")
    return output


def prepare_product_output_path(product_name, output_path):
    product_output = output_path / product_name
    product_output.mkdir()
    log.info(f"Preparing output path for {product_name}: {product_output.absolute()}")
    return product_output


async def prepare_order_books(method):
    # TODO: implement!
    log.info(f"Preparing orderbook using method: {method}")
    name = 'EXCHANGENAME_FROM_TO_TIMESTAMP'
    book = OrderBook(asks=[Ask(1, 2)], bids=[Bid(3, 4)])
    return {name: book}


async def start_redis(redis_server_cmd, product_output_path, loop):
    process = await asyncio.subprocess.create_subprocess_shell(
        cmd=f"{redis_server_cmd} --dir {product_output_path.absolute()}", stdout=asyncio.subprocess.DEVNULL)
    log.info(f"Started redis process: {process}")
    return process


async def connect_to_redis(loop):
    log.info("Connecting to redis")
    for i in range(10):
        try:
            return await aioredis.create_redis(address='redis://localhost', timeout=2.0, loop=loop)
        except OSError:
            log.debug("Redis is not ready yet...")
            await asyncio.sleep(0.2)


async def write_orderbooks_to_redis(redis, books):
    log.info("Writing orderbook to Redis")
    for name, book in books.items():
        log.debug(f"Setting: {name}: {orderbook_to_json(book)}")
        await redis.set(key=name, value=orderbook_to_json(book))

    log.debug("Saving Redis dump")
    await redis.save()


async def close_redis_connection(redis):
    log.info("Closing Redis connection")
    redis.close()
    await redis.wait_closed()
    # TODO: required?
    await asyncio.sleep(2)


def stop_redis(redis_process):
    log.info(f"Stopping Redis process: {redis_process}")
    redis_process.kill()


async def _main(redis_server_cmd, output_dir, loop):
    base_output_path = prepare_output_path(output_dir)

    for product in PRODUCTS:
        books = await prepare_order_books(product)
        product_output_path = prepare_product_output_path(product_name=product.name, output_path=base_output_path)
        redis_process = await start_redis(redis_server_cmd, product_output_path, loop)
        redis_connection = await connect_to_redis(loop)
        await write_orderbooks_to_redis(redis_connection, books)
        await close_redis_connection(redis_connection)
        stop_redis(redis_process)


def _run_on_loop(redis_server_cmd, output_dir=OUTPUT_PATH_BASE):
    log.debug('Starting event loop')
    loop = asyncio.get_event_loop()
    # try:
    loop.run_until_complete(_main(redis_server_cmd, output_dir, loop))
    # finally:
    # log.info('Closing event loop')
    # loop.close()


def _setup_logging():
    message_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(format=message_format, level=logging.DEBUG)
    logging.getLogger('asyncio').setLevel(logging.INFO)


if __name__ == '__main__':
    _setup_logging()

    log = logging.getLogger(__name__)

    fire.Fire(_run_on_loop)
