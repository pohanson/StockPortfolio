from typing import Union

from pymongo import MongoClient

from .mongo_client import get_mongo_client

class _StockDb:
    def __init__(self, client: MongoClient):
        self.coll = client["data"]["stock_data"]

    def find_one_stock(self, stock_code: str) -> Union[dict, None]:
        """Return the information about a particular stock.

        Args:
            stock_code (str): the stock code to search by

        Returns:
            Union[dict, None]: return None if invalid code is given.
        """
        return self.coll.find_one({"_id": stock_code})


stockdb = _StockDb(get_mongo_client())
