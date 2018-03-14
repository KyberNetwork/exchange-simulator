import pytest

from orderbookgenerator.generators.generators import (
    OrderBook,
    Bid,
    Ask,
    orderbook_to_json,
    StaticOrderBookGenerator,
    OrderBookGenerationParams,
    BlockRandomOrderBookGenerator
)

PARAMS = OrderBookGenerationParams(exchanges='A',
                                   tokens='B',
                                   base_token='C',
                                   timestamp_start=0,
                                   timestamp_stop=10,
                                   timestamp_step=1,
                                   min_quantity=0,
                                   max_quantity=10,
                                   min_rate=0,
                                   max_rate=10,
                                   number_of_asks=10,
                                   number_of_bids=10,
                                   middle_rate=5,
                                   rate_gap=1)


def test_to_json__empty():
    o = OrderBook(asks=[], bids=[])
    assert orderbook_to_json(o) == '{"Asks": [], "Bids": []}'


def test_to_json():
    asks = [Ask(quantity=1, rate=2)]
    bids = [Bid(quantity=3, rate=4)]
    o = OrderBook(asks=asks, bids=bids)

    j = orderbook_to_json(o)

    assert j == '{"Asks": [{"Quantity": 1, "Rate": 2}], "Bids": [{"Quantity": 3, "Rate": 4}]}'


@pytest.mark.asyncio
async def test_StaticOrderBookGenerator__number_of_bids_and_asks():
    params = PARAMS
    generator = StaticOrderBookGenerator(params)
    books = await generator.prepare_books()

    for _, book in books.items():
        assert len(book.asks) == params.number_of_asks
        assert len(book.bids) == params.number_of_bids


@pytest.mark.asyncio
async def test_StaticOrderBookGenerator__all_values_are_same():
    generator = StaticOrderBookGenerator(PARAMS)
    books = await generator.prepare_books()

    all_books = list(books.values())
    first = all_books[0]
    assert all(x == first for x in all_books)


@pytest.mark.asyncio
async def test_BlockRandomOrderBookGenerator__initial():
    generator = BlockRandomOrderBookGenerator(PARAMS, timestamp_step=2)
    books = await generator.prepare_books()

    assert books is not None


@pytest.mark.asyncio
async def test_BlockRandomOrderBookGenerator__initial():
    timestamp_step = 2
    generator = BlockRandomOrderBookGenerator(PARAMS, timestamp_step=timestamp_step)
    books = await generator.prepare_books()

    keys = sorted(books.keys())
    first_key_index = 0
    assert books[keys[first_key_index]] == books[keys[first_key_index + 1]]
    assert books[keys[first_key_index]] != books[keys[first_key_index + timestamp_step]]
    assert books[keys[first_key_index + timestamp_step]] == books[keys[first_key_index + timestamp_step + 1]]
