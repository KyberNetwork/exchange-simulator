import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import aioredis
import fire

from generator.orderbook import (
    orderbook_to_json,
    prepare_order_books
)

Product = namedtuple("Product", ["name", "method"])

PRODUCTS = [
    Product(name="Initial", method="STANDARD")
]

# TODO: Move to some "config" module
OUTPUT_PATH_BASE = "output"


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


async def start_redis(redis_server_cmd, product_output_path, loop, verbose=False):
    stdout = asyncio.subprocess.DEVNULL if not verbose else None
    process = await asyncio.subprocess.create_subprocess_shell(
        cmd=f"{redis_server_cmd} --dir {product_output_path.absolute()}", stdout=stdout)
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


async def _main(redis_server_cmd, output_dir, verbose, loop):
    base_output_path = prepare_output_path(output_dir)

    for product in PRODUCTS:
        books = await prepare_order_books(product)
        product_output_path = prepare_product_output_path(product_name=product.name, output_path=base_output_path)
        redis_process = await start_redis(redis_server_cmd, product_output_path, loop, verbose)
        redis_connection = await connect_to_redis(loop)
        await write_orderbooks_to_redis(redis_connection, books)
        await close_redis_connection(redis_connection)
        await stop_redis(redis_process)


def _run_on_loop(redis_server_cmd, output_dir=OUTPUT_PATH_BASE, verbose=False):
    log.debug('Starting event loop')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(redis_server_cmd, output_dir, verbose, loop))
    log.info('Closing event loop')


def _setup_logging():
    message_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(format=message_format, level=logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.INFO)


if __name__ == '__main__':
    _setup_logging()

    log = logging.getLogger(__name__)

    fire.Fire(_run_on_loop)
