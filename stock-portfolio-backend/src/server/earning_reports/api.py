import code

from flask import Blueprint, jsonify, request
from server.database.transactiondb import transactiondb
from server.stocks.service import get_stock_name

from .api_schema import DividendBreakdownItem, TransactionBreakdownItem
from .dividend_earnings import list_dividend_earnings, sum_dividend_earnings
from .service import split_transactions
from .transaction_earnings import (
    list_transaction_earnings,
    sum_transaction_earnings,
)

pnl_api_bp = Blueprint("pnl", __name__, url_prefix="pnl")


@pnl_api_bp.get("")
def get_pnl():
    """Calculate and get the profit and loss data.

    Only includes non-zero profit/loss. P/L comprises of dividends and transaction_breakdown
    [{code, name, transaction_earnings, dividend_earnings}]
    """
    userid = request.environ.get("userid")
    if userid is None:
        return jsonify({"error": "Unauthorized"}), 401

    all_transactions = transactiondb.find_all_transaction(
        filter_dict={"userid": userid}
    )

    transaction_list = split_transactions(all_transactions)
    results = []
    for code, transactions in transaction_list.items():
        transaction_earning_list = list_transaction_earnings(transactions)
        total_transaction_earnings = sum_transaction_earnings(
            transaction_earning_list
        )
        dividend_earning_list = list_dividend_earnings(transactions)
        total_dividend_earnings = sum_dividend_earnings(dividend_earning_list)

        results.append(
            {
                "code": code,
                "name": get_stock_name(code),
                "transaction_earnings": total_transaction_earnings,
                "dividend_earnings": total_dividend_earnings,
            }
        )

    return jsonify(results)


@pnl_api_bp.get("/<code>")
def get_pnl_for_code(code: str):
    transactions = transactiondb.find_all_transaction(
        filter_dict={"userid": request.environ.get("userid"), "code": code}
    )
    transaction_earning_list = list_transaction_earnings(transactions)
    dividend_earning_list = list_dividend_earnings(transactions)
    data = {
        "code": code,
        "name": get_stock_name(code),
        "transactions_breakdown": TransactionBreakdownItem(many=True).dump(
            transaction_earning_list
        ),
        "dividends_breakdown": DividendBreakdownItem(many=True).dump(
            dividend_earning_list
        ),
    }
    return jsonify(data)
