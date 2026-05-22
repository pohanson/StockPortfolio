import datetime as dt
import typing
from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd
from data_structure import SortedSet
from server.transactions.model import Transaction
from yfinance import Ticker


class _VolumeRecord(typing.TypedDict):
    date: dt.date
    volume: int


@dataclass(frozen=True)
class DividendEarningRecord:
    date: dt.date
    volume: int
    rate: float  # dividend per share

    @property
    def earnings(self) -> float:
        return self.volume * self.rate


def list_dividend_earnings(
    transactions: Iterable[Transaction],
):
    """Calculate the dividend earnings from a list of transactions of the same stock.

    Args:
        transactions: List of transactions for a specific stock code.
    """
    earning_list: list[DividendEarningRecord] = []
    volume_list = SortedSet[_VolumeRecord]("date")

    for transaction in transactions:
        if transaction.is_buy():
            volume_list.add(
                _VolumeRecord(date=transaction.date, volume=transaction.volume)
            )
        elif transaction.is_sell():
            if len(volume_list) == 0:
                continue
            volume_list.add(
                _VolumeRecord(
                    date=transaction.date,
                    volume=volume_list[-1]["volume"] - transaction.volume,
                )
            )

    transaction_list = list(transactions)
    ticker_symbol = transaction_list[0].code + ".SI"
    ticker = Ticker(ticker_symbol)
    dividends = ticker.get_dividends()
    cur_index = -1
    dividend_items = typing.cast(
        Iterable[tuple[pd.Timestamp, float]],
        dividends.items(),
    )
    for (
        dividend_date,
        dividend_per_share,
    ) in dividend_items:  # date is ex-div date
        # find the cur_transaction that is just before the dividend date
        while (
            cur_index < len(volume_list) - 1
            and volume_list[cur_index + 1]["date"] < dividend_date.date()
        ):
            # increment if next is still before
            cur_index += 1

        if cur_index >= len(volume_list):
            break
        if dividend_date.date() < volume_list[cur_index]["date"]:
            continue
        earning_list.append(
            DividendEarningRecord(
                date=dividend_date.date(),
                volume=volume_list[cur_index]["volume"],
                rate=dividend_per_share,
            )
        )

    return earning_list


def sum_dividend_earnings(
    dividend_earning_records: list[DividendEarningRecord],
) -> float:
    """Sum up the earnings from a list of dividend earning records."""
    return sum(record.earnings for record in dividend_earning_records)
