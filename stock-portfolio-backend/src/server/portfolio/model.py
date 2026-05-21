from dataclasses import dataclass
from typing import Iterable

from server.transactions.model import Transaction


@dataclass
class Holding:
    code: str
    volume: int
    cost: float

    @property
    def avg_price(self):
        if self.volume == 0:
            return 0
        return self.cost / self.volume


@dataclass
class Portfolio:
    userid: str
    code_holding_map: dict[str, Holding]  # code: Holding

    @property
    def holdings(self) -> Iterable[Holding]:
        return self.code_holding_map.values()

    @property
    def total_cost(self):
        return sum([h.cost for h in self.holdings])

    def add_transaction(self, transaction: Transaction):
        code = transaction.code
        holding = self.code_holding_map.get(code)
        if holding is None:
            holding = Holding(code=code, volume=0, cost=0)
            self.code_holding_map[code] = holding

        if transaction.type_ == "buy":
            holding.volume += transaction.volume
            holding.cost += (
                transaction.price * transaction.volume + transaction.fees
            )
        elif transaction.type_ == "sell":
            if holding.volume == transaction.volume:
                # fully sold, reset the holding
                holding.volume = 0
                holding.cost = 0
            else:
                percentage_sold = transaction.volume / holding.volume
                cost_reduction = round(holding.cost * percentage_sold, 2)

                holding.cost -= cost_reduction
                holding.volume -= transaction.volume
