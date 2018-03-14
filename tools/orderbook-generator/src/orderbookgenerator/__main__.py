import asyncio
import logging
import sys
from pathlib import Path

import fire


def _setup_logging():
    message_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(format=message_format, level=logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.INFO)


_setup_logging()
sys.path.insert(1, str(Path(__file__).parent.parent))

from orderbookgenerator import conductor


def _run_on_loop(redis_server_cmd, output_dir=conductor.OUTPUT_PATH_BASE, verbose=False):
    log.debug('Starting event loop')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conductor.main(redis_server_cmd, output_dir, verbose, loop))
    log.info('Closing event loop')


log = logging.getLogger(__name__)
fire.Fire(_run_on_loop)