import datetime as dt
from collections.abc import Iterable
from typing import TypedDict, cast

from server.transactions.model import Transaction


class TransactionBreakdownRecord(TypedDict):
    date: dt.date
    type_: str
    price: float
    volume: int
    earnings: float


def list_transaction_earnings(
    transactions: Iterable[Transaction],
) -> list[TransactionBreakdownRecord]:
    """Calculate the realised earnings from a list of transactions of the same stock.

    Args:
        transactions: List of transactions for a specific stock code.
    """
    sorted_transactions = sorted(transactions, key=lambda t: t.date)
    total_profit = 0
    cur_volume = 0
    cur_cost = 0

    transaction_earning_records: list[TransactionBreakdownRecord] = []
    for transaction in sorted_transactions:
        value = transaction.price * transaction.volume
        fees = transaction.calculate_fees()
        if transaction.type_ == "buy":
            cur_volume += transaction.volume
            cur_cost += value + fees
            transaction_earning_records.append(
                {
                    "date": transaction.date,
                    "type_": transaction.type_,
                    "price": transaction.price,
                    "volume": transaction.volume,
                    "earnings": 0,
                }
            )
        elif transaction.type_ == "sell":
            if cur_volume == transaction.volume:
                # fully sold
                earnings = value - fees - cur_cost
                cur_volume = 0
                cur_cost = 0

            else:
                # partially sold at average cost.
                percentage_cost = round(cur_cost / cur_volume * transaction.volume, 2)
                earnings = value - percentage_cost - fees
                cur_volume -= transaction.volume
                cur_cost -= percentage_cost

            total_profit += earnings
            transaction_earning_records.append(
                {
                    "date": transaction.date,
                    "type_": transaction.type_,
                    "price": transaction.price,
                    "volume": transaction.volume,
                    "earnings": earnings,
                }
            )
    return transaction_earning_records


def sum_transaction_earnings(
    transaction_earning_records: list[TransactionBreakdownRecord],
) -> float:
    """Sum up the earnings from a list of transaction earning records."""
    return sum(
        cast(float, record["earnings"]) for record in transaction_earning_records
    )
