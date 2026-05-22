import logging

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from .api_schema import (
    CreateTransactionSchema,
    NamedTransactionSchema,
    TransactionSchema,
)
from .model import Transaction
from .service import (
    get_all_transactions_by_userid,
    get_transaction_by_id,
    insert_transaction,
    update_transaction,
)

transaction_api_bp = Blueprint(
    "transaction", __name__, url_prefix="transaction"
)


log = logging.getLogger(__name__)


@transaction_api_bp.get("")
def get_transaction():
    """Get all the transaction for a user.

    The user is gotten indirectly from session linked to a user.

    Json Response:
        + 200 [{id, date, code, name, type_, price, volume, broker, last_modified}]
        + 400 {"error": str}
    """
    userid = request.environ.get("userid", None)
    if userid is None:
        return jsonify({"error": "No valid user"}), 400

    transactions = get_all_transactions_by_userid(userid)
    schema = NamedTransactionSchema(many=True)

    return jsonify(schema.dump(transactions))


@transaction_api_bp.get("/<transaction_id>")
def get_transaction_id(transaction_id):
    """Get a single transaction based on the id

    Json Response:
        + 200 {_id, date, code, type_, price, volume, broker, last_modified, name}
        + 404 {error: "No such transaction `transaction_id` was found"}
    """
    result = get_transaction_by_id(transaction_id)
    if result is None:
        return (
            jsonify(
                {"error": f"No such transaction '{transaction_id}' was found."}
            ),
            404,
        )
    schema = NamedTransactionSchema()
    return jsonify(schema.dump(result))


@transaction_api_bp.post("")
def post_transaction():
    """Create new transaction.

    Requires:
        json: {date, code, type_, price, volume, broker, last_modified}

    Json Response:
        + 200 {_id, date, code, type_, price, volume, broker, last_modified}
        + 400 {"error": str}
    """

    try:
        CreateTransactionSchema().validate(request.json)
    except ValidationError as e:
        log.error(e)
        return jsonify({"error": str(e)}), 400
    userid = request.environ.get("userid")
    if userid is None:
        return jsonify({"error": "Missing user"}), 400

    transaction = Transaction.from_dict(request.json)
    transaction.userid = userid
    data = insert_transaction(transaction)
    return jsonify(TransactionSchema().dump(data))


@transaction_api_bp.delete("/<transaction_id>")
def delete_transaction(transaction_id):
    """Delete a transaction

    Json Response:
        + 204 (no content) : successfully deleted
        + 404 {"error": "No such transaction `transaction_id` was found"}
    """
    result = delete_transaction(transaction_id)
    if result is None:
        return (
            jsonify(
                {"error": f"No such transaction '{transaction_id}' was found."}
            ),
            404,
        )
    return "", 204


@transaction_api_bp.put("/<transaction_id>")
def put_transaction(transaction_id):
    """Fully replace a transaction id with the current data

    Even fields that are not changed must still be provided

    Requires:
        + json: {date, code, type_, price, volume, broker, last_modified}

    Json Response:
        + 204 (no content): Successfully replaced
        + 400 {"error": str}
        + 404 {"error": "No such transaction `transaction_id` was found"}
    """
    try:
        TransactionSchema().validate(
            request.json,
            partial=["_id", "userid"],
        )

    except ValidationError as e:
        log.error(e)
        return jsonify({"error": str(e)}), 400
    transaction = Transaction.from_dict(request.json)
    transaction._id = transaction_id
    transaction.userid = request.environ.get("userid", "NULL_USER")

    result = update_transaction(transaction_id, transaction)

    if result is None:
        return (
            jsonify(
                {"error": f"No such transaction '{transaction_id}' was found."}
            ),
            404,
        )
    return "", 204
