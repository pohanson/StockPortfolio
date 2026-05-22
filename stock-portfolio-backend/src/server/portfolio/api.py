from flask import Blueprint, jsonify, request
from server.portfolio.api_schema import PortfolioSchema
from server.portfolio.service import calculate_portfolio

portfolio_api_bp = Blueprint("portfolio", __name__, url_prefix="portfolio")
portfolio_schema = PortfolioSchema()


@portfolio_api_bp.get("")
def get_portfolio():
    """Get the outstanding current holdings. ie. volume is not 0

    Json Response:
        + 200 [{code, name, volume, cost, avg_price, last}]
        + 400 {"error": str}
    """

    userid = request.environ.get("userid", None)
    if userid is None:
        return jsonify({"error": "No valid user"}), 400
    calculated_portfolio = calculate_portfolio(userid)
    holdings = portfolio_schema.dump(calculated_portfolio).get("holdings", [])

    return (jsonify(holdings), 200)
