from marshmallow import Schema, fields, post_dump


class PNLReportLineItem(Schema):
    code = fields.String()
    name = fields.String()
    transaction_earnings = fields.Float()
    dividend_earnings = fields.Float()


class TransactionBreakdownItem(Schema):
    date = fields.Date()
    type_ = fields.String()
    price = fields.Float()
    volume = fields.Integer()
    earnings = fields.Float()

    # TODO: instead of list, just send as json dict.
    @post_dump
    def to_list(self, data, **kwargs):
        keys = ["date", "type_", "price", "volume", "earnings"]
        return [data[k] for k in keys]


class DividendBreakdownItem(Schema):
    date = fields.Date()
    rate = fields.Float()
    volume = fields.Integer()
    earnings = fields.Float()

    # TODO: instead of list, just send as json dict.
    @post_dump
    def to_list(self, data, **kwargs):
        keys = ["date", "volume", "rate", "earnings"]
        return [data[k] for k in keys]
