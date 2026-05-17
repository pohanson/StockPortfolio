from flask import Blueprint

from server.apis.portfolio import portfolio_api_bp
from server.apis.profit_n_loss import pnl_api_bp
from server.apis.sync.sync_transactionapi import sync_transaction_api_bp
from server.transactions.api import transaction_api_bp
from server.apis.users.userapi import user_api_bp

api_bp = Blueprint("api", __name__, url_prefix="/api/v0")
api_bp.register_blueprint(transaction_api_bp)
api_bp.register_blueprint(user_api_bp)
api_bp.register_blueprint(pnl_api_bp)
api_bp.register_blueprint(portfolio_api_bp)
api_bp.register_blueprint(sync_transaction_api_bp)
