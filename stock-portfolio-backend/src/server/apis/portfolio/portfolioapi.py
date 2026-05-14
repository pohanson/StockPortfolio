from flask import Blueprint, jsonify, request
from yfinance import Tickers

from server.database.transactiondb import transactiondb
from server.model.stock_ledger import Ledger

portfolio_api_bp = Blueprint("portfolio", __name__, url_prefix="portfolio")


@portfolio_api_bp.get("")
def get_portfolio():
    """Get the outstanding current holdings. ie. volume is not 0

    Json Response:
        + 200 [{avg_price, code, cost, name, pnl, transactions_breakdown, transactions_sum, volume}]
        + 400 {"error": "No valid user"}


    """
    userid = request.environ.get("userid", None)
    if userid is None:
        return jsonify({"error": "No valid user"}), 400

    ledger = Ledger()
    ledger.add_transactions(
        transactiondb.find_all_transaction(filter_dict={"userid": userid})
    )

    json_data = []
    tickers = []
    # Filter out for current holdings
    for v in ledger.tabulate_transactions().values():
        if v["volume"] == 0:
            continue
        tickers.append(v["code"] + ".SI")
        json_data.append(v)

    tickers = Tickers(" ".join(tickers))

    for data in json_data:
        code = data["code"] + ".SI"
        data["last"] = tickers.tickers[code].get_info().get("currentPrice", 0)
    return jsonify(json_data)
