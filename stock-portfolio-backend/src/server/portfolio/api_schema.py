from marshmallow import Schema, fields, pre_dump
from yfinance import Tickers
from server.portfolio.model import Holding, Portfolio
from server.stocks.service import get_stock_name


class _HoldingSchema(Schema):
    code = fields.String(required=True)
    name = fields.Method("get_stock_name")
    volume = fields.Integer(required=True, strict=True)
    cost = fields.Float(required=True)  # total cost of holding
    avg_price = fields.Method("get_avg_price")
    last = fields.Method("get_last_price")

    def get_stock_name(self, o: Holding):
        stock_name = get_stock_name(o.code)
        if stock_name is None:
            return None
        else:
            return stock_name

    def get_last_price(self, o: Holding):
        tickers = Tickers(o.code + ".SI")
        return tickers.tickers[o.code + ".SI"].get_info().get("currentPrice", 0)

    def get_avg_price(self, o: Holding):
        return o.cost / o.volume if o.volume != 0 else 0


class PortfolioSchema(Schema):
    userid = fields.String(required=True)
    holdings = fields.List(fields.Nested(_HoldingSchema), required=True)
