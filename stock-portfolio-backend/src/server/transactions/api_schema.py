import datetime as dt

from marshmallow import (
    Schema,
    fields,
    post_dump,
    post_load,
    validate,
    validates,
)
from server.stocks.service import get_stock_name

from .model import Transaction


class TransactionSchema(Schema):
    _id = fields.String(required=True)
    date = fields.Date("iso", required=True)
    code = fields.String(required=True)
    type_ = fields.String(
        required=True,
        validate=validate.OneOf(["buy", "sell"], error="Invalid type_ selected."),
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Price should not be negative"),
    )
    volume = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
    )
    broker = fields.String(
        required=True,
        validate=validate.OneOf(["poems", "moomoo"]),
    )
    userid = fields.String(required=True)
    last_modified = fields.DateTime(
        "iso",
        load_default=lambda: dt.datetime.utcnow(),
    )

    @post_load
    def make_transaction(self, data, **kwargs):
        return Transaction(**data)

    @post_dump
    def post_dump(self, data, **kwargs):
        return data

    @validates("code")
    def validate_code(self, value, **kwargs):
        if get_stock_name(value) is None:
            raise ValueError("Invalid stock code given.")


class NamedTransactionSchema(TransactionSchema):
    # Includes the name of the stock
    name = fields.Method("get_stock_name")

    def get_stock_name(self, o: Transaction):
        stock_name = get_stock_name(o.code)
        if stock_name is None:
            return "Unknown Stock"
        else:
            return stock_name


class CreateTransactionSchema(TransactionSchema):
    class Meta:
        exclude = ("_id", "userid")
