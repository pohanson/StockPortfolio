from flask import Blueprint

from server.portfolio.portfolioapi import portfolio_api_bp as portfolio_api_bp_v0
from server.earning_reports.api import pnl_api_bp as pnl_api_bp_v0
from server.sync.sync_transactionapi import sync_transaction_api_bp
from server.transactions.api import transaction_api_bp
from server.users.userapi import user_api_bp

from server.portfolio.api import portfolio_api_bp as portfolio_api_bp_v1
from server.earning_reports.api import pnl_api_bp as pnl_api_bp_v1

api_bp = Blueprint("api", __name__, url_prefix="/api")
apiv0_bp = Blueprint("apiv0", __name__, url_prefix="/v0")
api_bp.register_blueprint(apiv0_bp)
apiv1_bp = Blueprint("apiv1", __name__, url_prefix="/v1")
api_bp.register_blueprint(apiv1_bp)

apiv0_bp.register_blueprint(transaction_api_bp)
apiv0_bp.register_blueprint(user_api_bp)
apiv0_bp.register_blueprint(pnl_api_bp_v0)
apiv0_bp.register_blueprint(portfolio_api_bp_v0)
apiv0_bp.register_blueprint(sync_transaction_api_bp)

apiv1_bp.register_blueprint(transaction_api_bp)
apiv1_bp.register_blueprint(user_api_bp)
apiv1_bp.register_blueprint(pnl_api_bp_v1)  # Breaking change
apiv1_bp.register_blueprint(portfolio_api_bp_v1)  # Breaking change
apiv1_bp.register_blueprint(sync_transaction_api_bp)
