import concurrent.futures
from typing import Any

from server.stocks.service import get_stock_name
from server.data_structure import SortedSet
from server.transactions.model import Transaction
from server.scraper.dividends.calculate_dividends import (
    calc_total_dividend_earnings,
)


class _StockRecord:
    """Helps to keep track of all the transaction of a single stock"""

    def __init__(self, code: str) -> None:
        self.code = code

        self.transaction_set: SortedSet[Transaction] = SortedSet("date")

    def __repr__(self) -> str:
        return f"StockRecord{self.code} [{self.transaction_set}]"

    @property
    def avg_price(self):
        if self.volume == 0:
            return 0
        return self.cost / self.volume

    @property
    def volume(self) -> int:
        """Current volume

        Returns:
            int: Number of vol of shares.
        """
        total_vol = 0
        for transaction in self.transaction_set:
            if transaction.type_ == "buy":
                total_vol += transaction.volume
            elif transaction.type_ == "sell":
                total_vol -= transaction.volume

        return total_vol

    def tabulate_transactions(self) -> dict[str, Any]:
        """Single pass to tabulate the transactions.

        Returns:
            dict[str, Any]: has keys: "code", "name", "volume", "cost", "transactions_sum", "transactions_breakdown"
        """
        # sum of all the transactions till sold fully.
        cur_total_cost = 0
        cur_total_volume = 0
        pnl = 0  # the net profit/loss when vol is zero, +ve is profit

        # (date, buy/sell, price, volume, value, net)
        transactions = []
        for transaction in self.transaction_set:
            value = transaction.price * transaction.volume
            fees = transaction.calculate_fees()

            if transaction.type_ == "buy":
                transactions.append(
                    [
                        transaction.date,
                        "buy",
                        transaction.price,
                        transaction.volume,
                        value + fees,
                        0,
                    ]
                )
                cur_total_cost += value + fees
                cur_total_volume += transaction.volume

            elif transaction.type_ == "sell":
                # net p/l for the cur transaction so far.
                # +ve means there is profit
                trans_net_pl = 0
                # check if fully sold
                if cur_total_volume == transaction.volume:
                    # fully sold
                    trans_net_pl = value - fees - cur_total_cost

                    # when fully sold, save to pnl and reset the cost and vol
                    pnl += trans_net_pl
                    cur_total_volume = 0
                    cur_total_cost = 0

                else:
                    # percentage of cost based on volume left
                    percentage_cost = (
                        cur_total_cost / cur_total_volume * transaction.volume
                    )
                    trans_net_pl = value - percentage_cost - fees

                    pnl += trans_net_pl
                    cur_total_volume -= transaction.volume
                    cur_total_cost -= percentage_cost

                transactions.append(
                    [
                        transaction.date,
                        "sell",
                        transaction.price,
                        transaction.volume,
                        value - fees,
                        trans_net_pl,
                    ]
                )

        return {
            "code": self.code,
            "name": get_stock_name(self.code),
            "volume": cur_total_volume,
            "cost": cur_total_cost,
            "avg_price": self.avg_price,
            "transactions_sum": pnl,
            # transactions_breakdown: list[list]
            # [date, buy/sell, price, volume, value, net]
            "transactions_breakdown": transactions,
        }

    @property
    def cost(self) -> float:
        total_cost = 0
        for transaction in self.transaction_set:
            value = transaction.price * transaction.volume
            total_cost += transaction.calculate_fees()
            if transaction.type_ == "buy":
                total_cost += value
            elif transaction.type_ == "sell":
                total_cost -= value
        return total_cost

    def add_transaction(self, transaction: Transaction) -> None:
        if transaction.code != self.code:
            raise TypeError(
                f"Stock {transaction.code} is added to {self.code} ledger"
            )
        self.transaction_set.add(transaction)

    def to_dict(self) -> dict[str, Any]:
        calculated_data = self.tabulate_transactions()
        dividends_sum, dividends_breakdown = calc_total_dividend_earnings(
            self.code, self.transaction_set
        )
        return {
            "code": self.code,
            "name": get_stock_name(self.code),
            "volume": calculated_data["volume"],
            "cost": calculated_data["cost"],
            "avg_price": self.avg_price,
            "pnl": calculated_data["transactions_sum"] + dividends_sum,
            # transactions_breakdown: list[list]
            # [date, buy/sell, price, volume, value, net]
            "transactions_breakdown": calculated_data["transactions_breakdown"],
            "transactions_sum": calculated_data["transactions_sum"],
            # dividend breakdown: list[list]][ex-date, rate, volume, value]
            "dividends_breakdown": dividends_breakdown,
            "dividends_sum": dividends_sum,
        }


class Ledger:
    def __init__(self) -> None:
        self.stock_recs: dict["str", _StockRecord] = {}  # code: rec

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.to_dict())

    def add_transaction(self, transaction: Transaction) -> None:
        if transaction.code not in self.stock_recs:
            self.stock_recs[transaction.code] = _StockRecord(transaction.code)
        self.stock_recs[transaction.code].add_transaction(transaction)

    def add_transactions(self, transactions: list[Transaction]) -> None:
        for transaction in transactions:
            self.add_transaction(transaction)

    def tabulate_transactions(self):
        return {
            k: v.tabulate_transactions() for k, v in self.stock_recs.items()
        }

    def to_dict(self) -> dict[str, dict[str, Any]]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            result = executor.map(
                lambda v: v.to_dict(), self.stock_recs.values()
            )

        return {k: v for k, v in zip(self.stock_recs.keys(), result)}

    def to_json(self) -> list[dict]:
        return self.to_dict().values()
