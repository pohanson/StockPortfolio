from flask import Blueprint, jsonify, request
from server.database.transactiondb import transactiondb
from server.model.stock_ledger import Ledger

pnl_api_bp = Blueprint("pnl", __name__, url_prefix="pnl")


@pnl_api_bp.get("")
def get_pnl():
    """Calculate and get the profit and loss data.

    Only includes non-zero profit/loss. P/L comprises of dividends and transaction_breakdown

    Json Response:
        + 200: [{code, name, volume, cost, avg_price, pnl, transactions_breakdown, transactions_sum, dividends_breakdown, dividends_sum}]
            + transactions_breakdown: [date, buy/sell, price, volume, value, net]
            + dividends_breakdown: [ex-date, rate, volume, value]
    """
    # get the net profit and loss data
    userid = request.environ.get("userid")

    ledger = Ledger()
    ledger.add_transactions(
        transactiondb.find_all_transaction(filter_dict={"userid": userid})
    )

    return jsonify([x for x in ledger.to_json() if x["pnl"] != 0])


@pnl_api_bp.get("/<code>")
def get_pnl_breakdown_by_code(code):
    """Get the breakdown for a specific code.

    Json Response:
        + 200: {code, name, volume, cost, avg_price, pnl, transactions_breakdown, transactions_sum, dividends_breakdown, dividends_sum}
            + transactions_breakdown: [date, buy/sell, price, volume, value, net]
            + dividends_breakdown: [ex-date, rate, volume, value]
    """
    userid = request.environ.get("userid")

    all_transactions = transactiondb.find_all_transaction(
        filter_dict={"userid": userid, "code": code}
    )
    # calculate buy and sell result
    ledger = Ledger()
    ledger.add_transactions(all_transactions)

    results = ledger.to_dict().get(code)

    # format the dates
    transactions_breakdown = results.get("transactions_breakdown", [])
    for result in transactions_breakdown:
        result[0] = result[0].strftime("%Y-%m-%d")

    dividends_breakdown = results.get("dividends_breakdown", [])
    for result in dividends_breakdown:
        result[0] = result[0].strftime("%Y-%m-%d")

    return jsonify(results)
