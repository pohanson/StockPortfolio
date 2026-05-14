import os
import secrets
import string
from datetime import datetime

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.results import UpdateResult

from server.model.transaction import Transaction
from .mongo_client import get_mongo_client

class _TransactionDb:
    def __init__(self, client: MongoClient):
        load_dotenv()
        if os.getenv("DEVELOPMENT_MODE") == "False":
            self.coll = client["data"]["transactions"]
            self.deleted_coll = client["data"]["deleted_transaction"]
        else:
            self.coll = client["test_data"]["transactions"]
            self.deleted_coll = client["test_data"]["deleted_transaction"]

    def insert_one_transaction(self, data: Transaction) -> dict:
        """Insert a transaction into database

        Args:
            data (Transaction): the transaction object to be inserted

        Returns:
            dict: the data inserted into the database
        """
        data = data.to_dict()
        transaction_id = self.generate_transaction_id()
        data["_id"] = transaction_id
        # remove deleted instances of same id
        self.deleted_coll.delete_many({"_id": transaction_id})
        self.coll.insert_one(data)
        return data

    def update_one_transaction(
        self, transaction_id: str, data: Transaction
    ) -> UpdateResult:
        """Update the transaction

        Args:
            transaction_id (str): Transaction _id to update
            data (Transaction): the transaction to insert

        Returns:
            UpdateResult
        """
        return self.coll.update_one({"_id": transaction_id}, {"$set": data.to_dict()})

    def upsert_one_transaction(
        self,
        transaction_id: str,
        userid: str,
        last_modified: datetime,
        data: Transaction,
    ) -> UpdateResult:
        """Update or Insert a Transaction

        Inserts transaction when the transaction _id and userid are not found.

        Updates the matching transaction _id and userid when the
        last_modified date is earlier than the new transaction

        Args:
            transaction_id (str): Transaction _id to upsert
            userid (str): the userid the transaction belongs to
            last_modified (datetime): last modified new transaction datetime
            data (Transaction): the transaction to upsert

        Returns:
            UpdateResult
        """
        # remove deleted instances
        self.deleted_coll.delete_many({"_id": transaction_id})
        return self.coll.update_one(
            {
                "_id": transaction_id,
                "last_modified": {"$lt": last_modified},
                "userid": userid,
            },
            {"$set": data.to_dict()},
            upsert=True,
        )

    def delete_transaction(self, transaction_id: str) -> Transaction:
        """Delete transaction by id, and insert that transaction into `deleted_transaction` collection

        Args:
            transaction_id (str): transaction id string to delete

        Returns:
            Transaction: the transaction that was deleted
        """
        deleted_transaction = self.coll.find_one_and_delete({"_id": transaction_id})
        if deleted_transaction is None:
            return
        # update last_modified to now
        deleted_transaction["last_modified"] = datetime.utcnow()
        self.deleted_coll.insert_one(deleted_transaction)
        return deleted_transaction

    def find_all_transaction(self, *, filter_dict={}) -> list[Transaction]:
        """Retrieve all transaction that matches an optional filter.

        By default, it will return all transaction.

        Args:
            filter_dict (dict, optional): Filter out transaction by a criteria.
                Defaults to {} which returns all transaction.

        Returns:
            list[Transaction]: all transaction that matches
        """
        data = [
            Transaction.from_dict(record)
            for record in self.coll.find(filter_dict).sort("date", pymongo.ASCENDING)
        ]
        return data

    def find_one_transaction(self, transaction_id: str):
        """Find and returns the transaction

        Args:
            transaction_id (str): the transaction id to find by

        Returns:
            Any | None: None if no transaction is found
        """
        return self.coll.find_one({"_id": transaction_id})

    def find_last_modified_after_transaction(
        self, userid: str, date: datetime
    ) -> list[Transaction]:
        """Find all transaction whose last_modified is after the `date`

        Args:
            userid (str): userid of that transaction
            date (datetime): transaction that is modified after this date

        Returns:
            list[Transaction]: list of transaction
        """
        return [
            Transaction.from_dict(record)
            for record in self.coll.find(
                {"last_modified": {"$gt": date}, "userid": userid}
            )
        ]

    def find_deleted_after_transaction(self, date: datetime) -> list[str]:
        """Find all transaction that is deleted after the `date`

        Args:
            date (datetime): transaction that is deleted after this date

        Returns:
            list[str]: all the transaction id of deleted transaction
        """
        return list(
            i["_id"]
            for i in self.deleted_coll.find(
                {"last_modified": {"$gt": date}}, {"_id": 1}
            )
        )

    @staticmethod
    def generate_transaction_id():
        return "".join(secrets.choice(string.ascii_lowercase) for _ in range(7))


transactiondb = _TransactionDb(get_mongo_client())
