from server.database.transactiondb import transactiondb
from .model import Transaction

def get_all_transactions_by_userid(userid):
    """Get all transactions for a user.

    Args:
        userid (str): The id of the user.
    Returns:
        list[Transaction]: list of transactions for the user.
    """
    transactions = transactiondb.find_all_transaction(filter_dict={"userid": userid})
    return transactions


def get_transaction_by_id(transaction_id):
    """Get a transaction by its id.

    Args:
        transaction_id (str): the id of the transaction

    Returns:
        Transaction | None: the transaction with the id, or None if not found
    """
    result = transactiondb.find_one_transaction(transaction_id)
    if result is None:
        return None
    return Transaction.from_dict(result)


def insert_transaction(transaction: Transaction) -> Transaction:
    """Insert a transaction to the database.

    Args:
        transaction (Transaction): the transaction to be inserted

    Returns:
        Transaction: the transaction that is inserted with id and last_modified
    """
    return Transaction.from_dict(transactiondb.insert_one_transaction(transaction))


def delete_transaction(transaction_id: str) -> Transaction | None:
    """Delete a transaction by id.

    Args:
        transaction_id (str): the id of the transaction to delete

    Returns:
        Transaction | None: the transaction that was deleted, or None if not found
    """
    result = transactiondb.delete_transaction(transaction_id)
    if result is None:
        return None
    return Transaction.from_dict(result)


def update_transaction(
    transaction_id: str, transaction: Transaction
) -> Transaction | None:
    """Update a transaction by id.

    Args:
        transaction_id (str): the id of the transaction to update
        new_data (dict): the new data to update the transaction with

    Returns:
        Transaction | None: the transaction that was updated, or None if not found
    """

    result = transactiondb.update_one_transaction(transaction_id, transaction)
    if not result.acknowledged:
        return None
    return get_transaction_by_id(transaction_id)
