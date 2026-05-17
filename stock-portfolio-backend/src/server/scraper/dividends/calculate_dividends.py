import datetime as dt
import sys
from dataclasses import dataclass
from typing import NamedTuple

import requests
from bs4 import BeautifulSoup, ResultSet, SoupStrainer

sys.path.append("src")
from server.transactions.model import Transaction

def _get_dividend_table_rows(stock_code) -> ResultSet:
    res = requests.get(f"https://www.dividends.sg/view/{stock_code}")

    dividend_html_table = SoupStrainer("table")
    soup = BeautifulSoup(
        res.text, "html.parser", parse_only=dividend_html_table
    )
    rows = soup.find_all("tr")
    if len(rows) == 0:
        return []
    rows.pop(0)

    return rows


class DividendDateRow(NamedTuple):
    rate: float
    exdate: dt.date


def _parse_table_rows(rows) -> list[DividendDateRow]:
    dividend_payouts: list[DividendDateRow] = []
    for row in rows:
        td_rows = row.find_all("td")
        if len(td_rows) < 4:
            # invalid row (example '1A4' ticker)
            continue
        rate, ex_date = td_rows[-4:-2]

        ex_date = dt.datetime.strptime(ex_date.get_text(), "%Y-%m-%d")
        if (
            ex_date >= dt.datetime(2015, 1, 1)
            and rate.get_text().strip() != "-"
        ):
            try:
                dividend_payouts.append(
                    DividendDateRow(
                        float(rate.get_text().strip("SGD ")), ex_date.date()
                    )
                )
            except ValueError:
                # when the rate is not in SGD
                continue

    return dividend_payouts


@dataclass
class TransactionVolumeRange:
    """Range is inclusive of start and exclusive of end"""

    start: dt.date
    end: dt.date
    volume: int

    def __contains__(self, value: DividendDateRow):
        return self.start <= value.exdate < self.end


def _generate_range_list(
    all_transactions: list[Transaction],
) -> list[TransactionVolumeRange]:
    complete_range_list: list[TransactionVolumeRange] = []
    incomplete_range: TransactionVolumeRange | None = None

    for transaction in all_transactions:
        if transaction.type_ == "buy":
            if incomplete_range is None:
                incomplete_range = TransactionVolumeRange(
                    transaction.date, None, transaction.volume
                )
            else:
                # 'finish' the range and open a new combined range
                incomplete_range.end = transaction.date
                complete_range_list.append(incomplete_range)
                incomplete_range = TransactionVolumeRange(
                    transaction.date,
                    None,
                    incomplete_range.volume + transaction.volume,
                )
        if transaction.type_ == "sell":
            incomplete_range.end = transaction.date
            if incomplete_range.volume == transaction.volume:
                complete_range_list.append(incomplete_range)
                incomplete_range = None
            else:
                incomplete_range.end = transaction.date
                complete_range_list.append(incomplete_range)
                incomplete_range = TransactionVolumeRange(
                    transaction.date,
                    None,
                    incomplete_range.volume - transaction.volume,
                )

    if incomplete_range is not None:
        complete_range_list.append(
            TransactionVolumeRange(
                incomplete_range.start,
                dt.date(5000, 1, 1),
                incomplete_range.volume,
            )
        )

    return complete_range_list


def get_dividends_earnings_breakdown(
    code: str, all_transactions: list[Transaction]
) -> list[tuple]:
    """Get the breakdown of the dividends

    Args:
        code (str): the code
        all_transactions (list[Transaction]): list of all transactions of that stock for that user

    Returns:
        list[list]: list of list [exdate, rate, volume, value]
        []: empty list if no dividend_rows is found
    """

    dividend_rows = _parse_table_rows(_get_dividend_table_rows(code))
    if len(dividend_rows) == 0:
        return []
    cur_row = dividend_rows.pop()
    breakdown = []
    for trans_range in _generate_range_list(all_transactions):
        # consume the rows till it reaches the start range
        while cur_row.exdate < trans_range.start and len(dividend_rows) > 0:
            cur_row = dividend_rows.pop()

        while cur_row in trans_range:
            breakdown.append(
                [
                    cur_row.exdate,
                    cur_row.rate,
                    trans_range.volume,
                    cur_row.rate * trans_range.volume,
                ]
            )
            if len(dividend_rows) == 0:
                break
            else:
                cur_row = dividend_rows.pop()
    return breakdown


def calc_total_dividend_earnings(
    code: str, all_transactions: list[Transaction]
) -> tuple:
    """Calculate and return the total sum from dividends and exact breakdown

    Args:
        code (str): the stock code
        all_transactions (list[Transaction]): list of all transactions of that stock for that user

    Returns:
        tuple: index 0 is the total sum. index 1 is the detailed breakdown
    """
    breakdown = get_dividends_earnings_breakdown(code, all_transactions)
    total_sum = sum(row[3] for row in breakdown)
    return (total_sum, breakdown)
