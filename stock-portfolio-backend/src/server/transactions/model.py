from __future__ import annotations

import datetime as dt
import json
from typing import Literal, Union

from ..stocks.stock_code_name_dict import stock_code_name_dict


class Transaction:
    def __init__(
        self,
        date: dt.date,
        code: str,
        type_: Literal["buy", "sell"],
        price: float,
        volume: int,
        broker: Literal["poems", "moomoo"],
        _id: str = "",
        userid: str = "NULL_USER",
        last_modified: dt.datetime | None = None,
    ):
        self.date: dt.date = date
        self.code: str = code
        self.broker = broker
        self.type_ = type_
        self.price: float = price
        self.volume: int = volume
        self._id: str = _id
        self.userid: str = userid
        self.last_modified: dt.datetime = (
            dt.datetime.utcnow() if last_modified is None else last_modified
        )

    def __repr__(self):
        return (
            f"Transaction {self._id if self._id is not None else ''}"
            f"({self.date.strftime('%Y-%m-%d')}, {self.code}, "
            f"{self.broker}, {self.type_}, {self.price}, {self.volume}, "
            f"{self.userid})"
        )

    def __eq__(self, __o: Union[str, Transaction]) -> bool:
        """Check if 2 transactions are equal. (they have the same id)

        Args:
            __o (Union[str, Transaction]): the str id or the transaction obj.

        Returns:
            bool: true if they are equal
        """
        if isinstance(__o, str):
            return self._id == __o
        elif isinstance(__o, Transaction):
            return self._id == __o._id

    def __getitem__(self, key):
        if key in [
            "date",
            "code",
            "broker",
            "type_",
            "price",
            "volume",
            "_id",
            "userid",
            "last_modified",
        ]:
            return self.__getattribute__(key)
        else:
            raise LookupError(f"Invalid key {key} is given.")

    def __hash__(self) -> int:
        _id_num_str = ""
        for c in self._id:
            _id_num_str += str(ord(c))
        return int(_id_num_str)

    @property
    def fees(self) -> float:
        return self.calculate_fees()

    def calculate_fees(self) -> float:
        """Calculate all the additional fees imposed by the broker.

        Returns:
            float: the total amount of the fees
        """
        value = self.price * self.volume
        clearing = round(0.0325 / 100 * value, 2)
        trading_access = round(0.0075 / 100 * value, 2)

        sub_sum = 0
        if self.broker == "poems":
            commission = max(25, 0.28 / 100 * value)
            settlement_instruction = 0.35
            sub_sum = sum(
                [commission, clearing, trading_access, settlement_instruction]
            )

        elif self.broker == "moomoo":
            commission = max(0.99, 0.03 / 100 * value)
            platform_fee = commission  # calculated in the same way
            sub_sum = sum([commission, platform_fee, clearing, trading_access])

        tax_rate_percentage = 7 if self.date < dt.date(2023, 1, 1) else 8
        tax = round(tax_rate_percentage / 100 * sub_sum, 2)
        return sum([sub_sum, tax])

    @classmethod
    def from_jsonstr(cls, json_str: str) -> "Transaction":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, _dict) -> "Transaction":
        # Ensure that date is of type date
        # It might be in datetime type when being retrieved from database
        if isinstance(_dict.get("date"), dt.datetime):
            _dict["date"] = _dict["date"].date()
        elif isinstance(_dict.get("date"), str):
            _dict["date"] = dt.datetime.strptime(_dict["date"], "%Y-%m-%d").date()

        return cls(**_dict)

    def update_last_modified_now(self):
        self.last_modified = dt.datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "date": dt.datetime.combine(self.date, dt.time(0, 0)),
            "code": self.code,
            "broker": self.broker,
            "type_": self.type_,
            "price": self.price,
            "volume": self.volume,
            "_id": self._id,
            "userid": self.userid,
            "last_modified": self.last_modified,
        }

    def to_json(self):
        data = self.to_dict()
        data["date"] = data["date"].strftime("%Y-%m-%d")
        data["last_modified"] = data["last_modified"].isoformat() + "Z"
        data["name"] = stock_code_name_dict[self.code]
        data.pop("userid")
        return data
