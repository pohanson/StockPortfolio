from data_structure import SortedSet
from server.transactions.model import Transaction


def split_transactions(
    transactions: list[Transaction],
) -> dict[str, SortedSet[Transaction]]:
    """Split transactions into list of transactions of the same stock code."""
    transactions_by_code = {}
    for transaction in transactions:
        stock_code = transaction.code
        if stock_code not in transactions_by_code:
            transactions_by_code[stock_code] = SortedSet("date")
        transactions_by_code[stock_code].add(transaction)
    return transactions_by_code
