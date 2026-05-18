from .model import Holding, Portfolio
from server.transactions.service import get_all_transactions_by_userid


def calculate_portfolio(userid: str) -> Portfolio:
    portfolio = Portfolio(userid=userid, code_holding_map={})
    for transaction in get_all_transactions_by_userid(userid):
        portfolio.add_transaction(transaction)
    return portfolio
