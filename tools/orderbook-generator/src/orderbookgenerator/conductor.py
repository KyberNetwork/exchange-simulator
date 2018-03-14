import asyncio
import logging
import random
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import aioredis

from orderbookgenerator.generators.generators import (
    orderbook_to_json,
    OrderBookGenerationParams,
    BlockRandomOrderBookGenerator,
    StaticOrderBookGenerator
)
from orderbookgenerator.generators.ten_percent_increase import TenPercentIncreaseOrderBookGenerator

Product = namedtuple("Product", ["name", "generator"])

# TODO: Move to some "config" module
OUTPUT_PATH_BASE = "output"

REDIS_PORT = random.randrange(start=49152, stop=65535)

EXCHANGES = ["binance"]
TOKENS = [
    "OMG",
    "KNC",
    "EOS",
    "SNT",
    "ELF",
    "POWR",
    "MANA",
    "BAT",
    "REQ",
    "GTO",
    "ENG",
    "SALT",
    "RDN",
    "APPC",
]
BASE_TOKEN = 'ETH'

RESERVE_INITIALIZE_TIME_IN_MILLIS = 5 * 60 * 1_000

log = logging.getLogger(__name__)


def _calculate_timestamp_stop(timestamp_start, test_time_in_seconds, additional_time=RESERVE_INITIALIZE_TIME_IN_MILLIS):
    return timestamp_start + additional_time + test_time_in_seconds * 1_000


MIN_QUANTITY = 0.1
MAX_QUANTITY = 30

MIN_RATE = 0.000_000_1
MAX_RATE = 1

NUMBER_OF_ASKS = 50
NUMBER_OF_BIDS = 50

MIDDLE_RATE = 0.05
RATE_GAP = 0.001

TIMESTAMP_START = 1518215100000
INITIAL_GENERATION_PARAMS = OrderBookGenerationParams(exchanges=EXCHANGES, tokens=TOKENS, base_token=BASE_TOKEN,
                                                      timestamp_start=TIMESTAMP_START,
                                                      timestamp_stop=_calculate_timestamp_stop(
                                                          timestamp_start=TIMESTAMP_START, test_time_in_seconds=5 * 60),
                                                      timestamp_step=10_000,
                                                      min_quantity=MIN_QUANTITY, max_quantity=MAX_QUANTITY,
                                                      min_rate=MIN_RATE, max_rate=MAX_RATE,
                                                      number_of_asks=NUMBER_OF_ASKS, number_of_bids=NUMBER_OF_BIDS,
                                                      middle_rate=MIDDLE_RATE, rate_gap=RATE_GAP)

STATIC_GENERATION_PARAMS = OrderBookGenerationParams(exchanges=EXCHANGES, tokens=TOKENS, base_token=BASE_TOKEN,
                                                     timestamp_start=TIMESTAMP_START,
                                                     timestamp_stop=_calculate_timestamp_stop(
                                                         timestamp_start=TIMESTAMP_START,
                                                         test_time_in_seconds=10),
                                                     timestamp_step=10_000,
                                                     min_quantity=MIN_QUANTITY, max_quantity=MAX_QUANTITY,
                                                     min_rate=MIN_RATE, max_rate=MAX_RATE,
                                                     number_of_asks=NUMBER_OF_ASKS, number_of_bids=NUMBER_OF_BIDS,
                                                     middle_rate=MIDDLE_RATE, rate_gap=RATE_GAP)

TEN_PERCENT_INCREASE_PARAMS = OrderBookGenerationParams(exchanges=EXCHANGES, tokens=TOKENS, base_token=BASE_TOKEN,
                                                        timestamp_start=TIMESTAMP_START,
                                                        timestamp_stop=_calculate_timestamp_stop(
                                                            timestamp_start=TIMESTAMP_START,
                                                            test_time_in_seconds=10),
                                                        timestamp_step=10_000,
                                                        min_quantity=MIN_QUANTITY, max_quantity=MAX_QUANTITY,
                                                        min_rate=MIN_RATE, max_rate=MAX_RATE,
                                                        number_of_asks=NUMBER_OF_ASKS, number_of_bids=NUMBER_OF_BIDS,
                                                        middle_rate=MIDDLE_RATE, rate_gap=RATE_GAP)

PRODUCTS = [
    Product(name="RandomBlocks",
            generator=BlockRandomOrderBookGenerator(params=INITIAL_GENERATION_PARAMS, timestamp_step=30_000)),
    Product(name="StaticRandom", generator=StaticOrderBookGenerator(params=STATIC_GENERATION_PARAMS)),
    Product(name="TenPercentIncrease",
            generator=TenPercentIncreaseOrderBookGenerator(params=TEN_PERCENT_INCREASE_PARAMS))
]


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
    log.info(f"Preparing output path: {product_output.absolute()}")
    return product_output


async def start_redis(redis_server_cmd, product_output_path, verbose):
    process = await asyncio.subprocess.create_subprocess_shell(
        cmd=f'{redis_server_cmd} --dir {product_output_path.absolute()} --port {REDIS_PORT}',
        stdout=None if verbose else asyncio.subprocess.DEVNULL)
    if process.returncode is not None and process.returncode != 0:
        log.error(f"Error starting Redis server.\nError code: {process.returncode}\nOutput: {process.stdout}")
        sys.exit(1)
    log.info(f"Started redis process: {process} on port {REDIS_PORT}")
    return process


async def connect_to_redis(loop):
    log.info("Connecting to redis")
    for i in range(10):
        try:
            return await aioredis.create_redis(address=f'redis://localhost:{REDIS_PORT}', timeout=2.0, loop=loop)
        except OSError:
            log.debug("Redis is not ready yet...")
            await asyncio.sleep(0.2)


async def write_orderbooks_to_redis(redis, books):
    log.info("Writing orderbook to Redis")
    for name, book in books.items():
        log.debug(f"Setting: {name}: {orderbook_to_json(book)}")
        await redis.set(key=name, value=orderbook_to_json(book))
    log.info(f"Wrote {len(books)} order books.")

    log.debug("Saving Redis dump")
    await redis.save()


async def close_redis_connection(redis):
    log.info("Closing Redis connection")
    redis.close()
    await redis.wait_closed()


async def stop_redis(redis_process):
    log.info(f"Stopping Redis process: {redis_process}")
    try:
        redis_process.kill()
        await redis_process.wait()
    except ProcessLookupError:
        log.warning(f"Cannot find Redis process: {redis_process}")


async def main(redis_server_cmd, output_dir, verbose, loop):
    base_output_path = prepare_output_path(output_dir)

    for product in PRODUCTS:
        log.info(f'Handling product {product.name}:')
        log.info(f'Order Book description: {product.generator}')
        books = await product.generator.prepare_books()
        product_output_path = prepare_product_output_path(product_name=product.name, output_path=base_output_path)
        redis_process = await start_redis(redis_server_cmd, product_output_path, verbose)
        redis_connection = await connect_to_redis(loop)
        await write_orderbooks_to_redis(redis_connection, books)
        await close_redis_connection(redis_connection)
        await stop_redis(redis_process)
