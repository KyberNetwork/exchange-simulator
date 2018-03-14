import pytest

from orderbookgenerator.generators.generators import (
    OrderBookGenerationParams,
    OrderBook,
    Ask,
    Bid
)
from orderbookgenerator.generators.ten_percent_increase import (
    TenPercentIncreaseOrderBookGenerator,
    Stage,
)

PARAMS = OrderBookGenerationParams(exchanges=['A'],
                                   tokens='B',
                                   base_token='C',
                                   timestamp_start=0,
                                   timestamp_stop=Stage.END.calculate_timestamp(timestamp_start=0),
                                   timestamp_step=10_000,
                                   min_quantity=0,
                                   max_quantity=10,
                                   min_rate=0,
                                   max_rate=10,
                                   number_of_asks=10,
                                   number_of_bids=10,
                                   middle_rate=5,
                                   rate_gap=1)


@pytest.mark.asyncio
async def test_prepare_books__initial():
    generator = TenPercentIncreaseOrderBookGenerator(PARAMS)
    books = await generator.prepare_books()

    assert books is not None


def _get_modified_order_book(orderbook, modify):
    return OrderBook(
        asks=[
            Ask(ask.quantity, modify(ask.rate))
            for ask in orderbook.asks
        ],
        bids=[
            Bid(bid.quantity, modify(bid.rate))
            for bid in orderbook.bids
        ],
    )


@pytest.mark.asyncio
async def test_prepare_books__initial():
    params = PARAMS
    generator = TenPercentIncreaseOrderBookGenerator(params)
    books = await generator.prepare_books()

    key_start = f"A_b_c_{params.timestamp_start}"
    key_take_first_rate = f"A_b_c_{Stage.TAKE_FIRST_RATE.calculate_timestamp(params.timestamp_start)}"
    key_take_second_rate = f"A_b_c_{Stage.TAKE_SECOND_RATE.calculate_timestamp(params.timestamp_start)}"

    assert books[key_start] == books[key_take_first_rate]
    assert books[key_take_second_rate] == _get_modified_order_book(orderbook=books[key_take_first_rate],
                                                                   modify=lambda x: x + params.middle_rate * 0.1)
