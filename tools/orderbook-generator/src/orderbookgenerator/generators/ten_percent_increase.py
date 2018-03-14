from datetime import timedelta
from enum import Enum, auto, unique
from itertools import accumulate

from orderbookgenerator.generators.generators import (
    OrderBookGenerator,
    prepare_random_order_book_from_params,
    prepare_book_name,
    OrderBook,
    Ask,
    Bid
)


@unique
class Stage(Enum):
    # Values need to be unique so adding auto() to make a unique tuple
    START = timedelta(minutes=0), auto()
    INITIALIZE_TIME = timedelta(minutes=5), auto()
    START_TESTING = timedelta(minutes=0), auto()
    TAKE_FIRST_RATE = timedelta(minutes=0), auto()
    WAIT_BEFORE_RATES_MODIFICATION = timedelta(minutes=1), auto()
    MODIFY_RATES = timedelta(minutes=0), auto()
    WAIT_FOR_PRICE_TO_STABILIZE = timedelta(minutes=6), auto()
    TAKE_SECOND_RATE = timedelta(minutes=0), auto()
    WAIT_BEFORE_END = timedelta(minutes=1), auto()
    END = timedelta(minutes=0), auto()

    def calculate_timestamp(self, timestamp_start):
        return timestamp_start + int(ACCUMULATED_TIME_UNTIL_STAGE[self].total_seconds()) * 1_000


TEST_STAGES = [
    Stage.START,
    Stage.INITIALIZE_TIME,
    Stage.START_TESTING,
    Stage.TAKE_FIRST_RATE,
    Stage.WAIT_BEFORE_RATES_MODIFICATION,
    Stage.MODIFY_RATES,
    Stage.WAIT_FOR_PRICE_TO_STABILIZE,
    Stage.TAKE_SECOND_RATE,
    Stage.WAIT_BEFORE_END,
    Stage.END,
]

_ACCUMULATED_TIME_DELTAS = list(accumulate((stage.value[0] for stage in TEST_STAGES)))

ACCUMULATED_TIME_UNTIL_STAGE = {
    stage: accumulated_time
    for stage, accumulated_time in
    zip(TEST_STAGES, _ACCUMULATED_TIME_DELTAS)
}


class TenPercentIncreaseOrderBookGenerator(OrderBookGenerator):
    def __str__(self):
        start = self.params.timestamp_start
        return f"{self.__class__.__name__}(" \
               f"start={start}, " \
               f"start_testing={Stage.START_TESTING.calculate_timestamp(start)}, " \
               f"take_first_rate={Stage.TAKE_FIRST_RATE.calculate_timestamp(start)}, " \
               f"take_second_rate={Stage.TAKE_SECOND_RATE.calculate_timestamp(start)}, " \
               f"stop={Stage.END.calculate_timestamp(self.params.timestamp_start)})"

    async def prepare_books(self):
        books = {}
        initial_order_book = prepare_random_order_book_from_params(self.params)
        modified_order_book = _prepare_order_book_with_modified_rates(
            order_book=initial_order_book,
            modifier=lambda x: x + 0.1 * self.params.middle_rate
        )

        first_section_start = Stage.START.calculate_timestamp(self.params.timestamp_start)
        first_section_stop = Stage.WAIT_BEFORE_RATES_MODIFICATION.calculate_timestamp(self.params.timestamp_start)

        second_section_start = Stage.MODIFY_RATES.calculate_timestamp(self.params.timestamp_start)
        second_section_stop = Stage.END.calculate_timestamp(self.params.timestamp_start)

        for exchange in self.params.exchanges:
            for token in self.params.tokens:
                _add_identical_order_books(order_book=initial_order_book, books=books,
                                           exchange=exchange, token=token, base_token=self.params.base_token,
                                           timestamp_start=first_section_start,
                                           timestamp_stop=first_section_stop,
                                           timestamp_step=self.params.timestamp_step)
                _add_identical_order_books(order_book=modified_order_book, books=books,
                                           exchange=exchange, token=token, base_token=self.params.base_token,
                                           timestamp_start=second_section_start,
                                           timestamp_stop=second_section_stop,
                                           timestamp_step=self.params.timestamp_step)

        return books


def _add_identical_order_books(order_book, books, exchange, token, base_token, timestamp_start, timestamp_stop,
                               timestamp_step):
    for timestamp in range(timestamp_start, timestamp_stop, timestamp_step):
        books[prepare_book_name(exchange, token, base_token, timestamp)] = order_book


def _prepare_order_book_with_modified_rates(order_book, modifier):
    return OrderBook(
        asks=[
            Ask(quantity=ask.quantity, rate=modifier(ask.rate))
            for ask in order_book.asks
        ],
        bids=[
            Bid(quantity=bid.quantity, rate=modifier(bid.rate))
            for bid in order_book.bids
        ]
    )