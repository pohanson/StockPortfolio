import datetime
import unittest

from marshmallow import ValidationError
from src.server.model.transaction import Transaction
from src.server.model.transaction_schema import TransactionSchema

transaction_schema = TransactionSchema()


class TransactionTestCase(unittest.TestCase):
    def test_to_from_dict(self):
        current_datetime = datetime.datetime.now()
        trans_dict_original = {
            "date": datetime.datetime(2020, 12, 11, 0, 0),
            "code": "AZG",
            "type_": "buy",
            "price": 1.1,
            "volume": 1000,
            "userid": "412",
            "broker": "poems",
            "_id": "pydqluk",
            "last_modified": current_datetime.isoformat(),
        }

        trans_json = trans_dict_original.copy()
        trans_json["date"] = "2020-12-11"

        trans = transaction_schema.load(trans_json)
        trans_dict_result = trans.to_dict()

        # Convert the last_modified into datetime obj
        trans_dict_original["last_modified"] = current_datetime

        self.assertEqual(trans_dict_original, trans_dict_result)

    def test_to_json(self):
        trans = Transaction.from_dict(
            {
                "date": datetime.datetime(2020, 12, 21, 0, 0),
                "code": "AZG",
                "type_": "buy",
                "price": 1.1,
                "volume": 1000,
                "userid": "412",
                "broker": "poems",
                "_id": "pydqluk",
            }
        )
        trans_json_result = trans.to_json()
        expected = {
            "_id": "pydqluk",
            "date": "2020-12-21",
            "code": "AZG",
            "type_": "buy",
            "price": 1.1,
            "volume": 1000,
            "broker": "poems",
            "name": "8Telecom",
        }

        for k, v in expected.items():
            self.assertEqual(v, trans_json_result[k], msg=k)

    def test_calc_poems_fees(self):
        trans = transaction_schema.load(
            {
                "date": "2020-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 1.12,
                "volume": 3000,
                "userid": "412",
                "broker": "poems",
                "_id": "pydqluk",
            }
        )

        # 7% gst
        self.assertAlmostEqual(28.56, trans.fees)

        # 8% gst
        trans.date = datetime.date(2023, 1, 1)
        self.assertAlmostEqual(28.83, trans.fees)

    def test_calc_moomoo_fees(self):
        trans = transaction_schema.load(
            {
                "date": "2020-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "moomoo",
                "_id": "pydqluk",
            }
        )
        # 7% gst
        self.assertAlmostEqual(2.85, trans.fees)

        # 8% gst
        trans.date = datetime.date(2023, 1, 1)
        self.assertAlmostEqual(2.87, trans.fees)

    def test_date_input(self):
        # Valid date
        transaction_schema.load(
            {
                "date": "2020-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "moomoo",
                "_id": "pydqluk",
            }
        )

        # Invalid date format
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "21/12/2020",
                    "code": "AZG",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "moomoo",
                    "_id": "pydqluk",
                }
            )

        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("date", ctx.exception.messages_dict.keys())

        with self.assertRaises(ValidationError, msg="msg") as ctx:
            transaction_schema.load(
                {
                    "date": "2020/12/21",
                    "code": "AZG",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "moomoo",
                    "_id": "pydqluk",
                }
            )
        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("date", ctx.exception.messages_dict.keys())

    def test_code_input(self):
        # invalid code
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZ2SH5G",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "poems",
                    "_id": "pydqluk",
                }
            )
        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("code", ctx.exception.messages_dict.keys())

    def test_broker_input(self):
        # valid broker
        transaction_schema.load(
            {
                "date": "2000-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "poems",
                "_id": "pydqluk",
            }
        )
        transaction_schema.load(
            {
                "date": "2000-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "moomoo",
                "_id": "pydqluk",
            }
        )

        # invalid broker
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZG",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "poemoo",
                    "_id": "pydqluk",
                }
            )

        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("broker", ctx.exception.messages_dict.keys())

    def test_type_input(self):
        # valid type_
        transaction_schema.load(
            {
                "date": "2000-12-21",
                "code": "AZG",
                "type_": "sell",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "poems",
                "_id": "pydqluk",
            }
        )
        transaction_schema.load(
            {
                "date": "2000-12-21",
                "code": "AZG",
                "type_": "buy",
                "price": 0.34,
                "volume": 5000,
                "userid": "412",
                "broker": "poems",
                "_id": "pydqluk",
            }
        )

        # invalid type_
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZG",
                    "type_": "bell",
                    "price": 0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "poems",
                    "_id": "pydqluk",
                }
            )
        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("type_", ctx.exception.messages_dict.keys())

    def test_price_input(self):
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZG",
                    "type_": "buy",
                    "price": -0.34,
                    "volume": 5000,
                    "userid": "412",
                    "broker": "moomoo",
                    "_id": "pydqluk",
                }
            )

        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("price", ctx.exception.messages_dict.keys())

    def test_volume_input(self):
        # invalid volume
        # negative volume
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZG",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": -5000,
                    "userid": "412",
                    "broker": "poems",
                    "_id": "pydqluk",
                }
            )
        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("volume", ctx.exception.messages_dict.keys())

        # not integer volume
        with self.assertRaises(ValidationError) as ctx:
            transaction_schema.load(
                {
                    "date": "2000-12-21",
                    "code": "AZG",
                    "type_": "buy",
                    "price": 0.34,
                    "volume": -5000,
                    "userid": "412",
                    "broker": "poems",
                    "_id": "pydqluk",
                }
            )
        self.assertEqual(1, len(ctx.exception.messages_dict.keys()))
        self.assertIn("volume", ctx.exception.messages_dict.keys())
