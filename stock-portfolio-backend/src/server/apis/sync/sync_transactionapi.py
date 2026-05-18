from datetime import datetime

from flask import Blueprint, jsonify, request

from server.database.transactiondb import transactiondb
from server.transactions.model import Transaction
from server.transactions.api_schema import TransactionSchema

sync_transaction_api_bp = Blueprint(
    "sync_transaction", __name__, url_prefix="sync/transaction"
)


@sync_transaction_api_bp.post("")
def sync_transaction():
    """Sync the transactions log

    Requires:
        json: {"deleted_transaction", "modified_transaction", "last_synced_datetime"}
            + deleted_transaction: [(transaction_id: str, last_modified: ISO8601 str)]
            + modified_transaction: [{_id, date, code, type_, price, volume, broker, last_modified}]
            + last_synced_datetime: ISO8601 str

    Json Response:
        + 200 {"deleted_transaction", "modified_transaction", "last_synced_datetime"}
            + deleted_transaction: [(transaction_id: str, last_modified: ISO8601 str)]
            + modified_transaction: [{_id, date, code, type_, price, volume, broker, last_modified}]
            + last_synced_datetime: ISO8601 str
    """
    deleted_transaction = request.json["deleted_transaction"]
    modified_transaction = request.json["modified_transaction"]
    last_synced_datetime = datetime.fromisoformat(
        request.json["last_synced_datetime"]
    )

    # get the userid
    userid = request.environ.get("userid")

    # search for duplicate id and remove transaction from one of them
    # lastest last_modified take precedence
    # if both have same, update takes precedence
    del_transaction_id_modified_map = {
        t[0]: t[1] for t in deleted_transaction
    }  # id: last_modified
    mod_transaction_id_map: dict[str, dict] = {
        transaction["_id"]: transaction for transaction in modified_transaction
    }  # id: transaction
    del_transaction_id_set = set(del_transaction_id_modified_map.keys())
    mod_transaction_id_set = set(mod_transaction_id_map.keys())
    intersection_id = del_transaction_id_set.intersection(
        mod_transaction_id_set
    )
    # compare timestamp
    for transaction_id in intersection_id:
        # if `modified_transaction` is later or equal to `deleted_transaction` timestamp, delete `deleted_transaction`
        if (
            mod_transaction_id_map[transaction_id]["last_modified"]
            >= del_transaction_id_modified_map[transaction_id]
        ):
            del_transaction_id_modified_map.pop(transaction_id)
        else:
            mod_transaction_id_map.pop("_id")

    # delete transactions in the db
    for transaction_id in del_transaction_id_modified_map:
        transactiondb.delete_transaction(transaction_id)

    # update/insert the modified transactions
    for t in mod_transaction_id_map.values():
        t.update(userid=userid)
        transaction: Transaction = TransactionSchema().load(t)
        transaction.update_last_modified_now()  # update the last modified time
        transactiondb.upsert_one_transaction_by_id_before_datetime(
            transaction_id=transaction._id,
            userid=transaction.userid,
            last_modified=transaction.last_modified,
            data=transaction,
        )

    # get updated transactions that is not updated from the current sync
    updated_from_synced_ids = del_transaction_id_set.union(
        mod_transaction_id_set
    )
    # get the new/updated transactions based on last_synced_datetime
    unsynced_modified_transactions = list(
        transaction
        for transaction in transactiondb.find_last_modified_after_transaction(
            userid=userid, date=last_synced_datetime
        )
        if transaction._id not in updated_from_synced_ids
    )
    # get the deleted transactions
    unsynced_deleted_transactions = list(
        _id
        for _id in transactiondb.find_deleted_after_transaction(
            last_synced_datetime
        )
    )

    # get updated transactions that is not updated from the current sync
    updated_from_synced_ids = del_transaction_id_set.union(
        mod_transaction_id_set
    )
    # get the new/updated transactions based on last_synced_datetime
    unsynced_modified_transactions = list(
        transaction
        for transaction in transactiondb.find_last_modified_after_transaction(
            userid=userid, date=last_synced_datetime
        )
        if transaction._id not in updated_from_synced_ids
    )
    # get the deleted transactions
    unsynced_deleted_transactions = list(
        _id
        for _id in transactiondb.find_deleted_after_transaction(
            last_synced_datetime
        )
        if _id not in updated_from_synced_ids
    )
    last_synced_datetime = datetime.utcnow().isoformat() + "Z"
    return jsonify(
        {
            "deleted_transaction": unsynced_deleted_transactions,
            "modified_transaction": [
                transaction.to_json()
                for transaction in unsynced_modified_transactions
            ],
            "last_synced_datetime": last_synced_datetime,
        }
    )
