import os

from argon2 import PasswordHasher
from dotenv import load_dotenv
from pymongo import MongoClient

from .mongo_client import get_mongo_client

class _UserDb:
    ph = PasswordHasher()

    def __init__(self, client: MongoClient):
        load_dotenv()
        if os.getenv("DEVELOPMENT_MODE") == "False":
            self.coll = client["data"]["user_info"]
        else:
            self.coll = client["test_data"]["user_info"]

        self.coll.create_index("username", unique=True)

    @staticmethod
    def check_missing_fields(user_data: dict, required_fields: list):
        """Checks for missing fields and raises error for missing fields.

        Args:
            user_data (dict): the data to check

        Raises:
            ValueError: If there is missing fields
        """
        missing_fields = []
        for field in required_fields:
            if field not in user_data:
                missing_fields.append(field)
        if len(missing_fields) > 0:
            raise ValueError(f"Missing Field {missing_fields}")

    def is_username_present(self, username: str) -> bool:
        """Check if username is in db. Return True when present

        Args:
            username (str): username

        Returns:
            bool: True when username is present
        """
        return self.coll.count_documents({"username": username}) != 0

    def insert_one_user(self, user_data: dict) -> str:
        """Validates and insert user

        Args:
            user_data (dict): contains keys ["username", "password", "name"]

        Raises:
            ValueError: Username is already used or field is missing

        Returns:
            str: _id of the user
        """
        # validation of data
        self.check_missing_fields(user_data, ["username", "password", "name"])

        # check if username is already used
        if self.is_username_present(user_data["username"]):
            raise ValueError(f"Username already exists {user_data['username']}")

        hashed_pw = self.ph.hash(user_data["password"])
        user_data["password"] = hashed_pw
        result = self.coll.insert_one(user_data)
        return str(result.inserted_id)

    def find_one_user(self, username: str, show_password=False) -> dict:
        """Find and returns a user based on username

        Args:
            username (str): username to find
            show_password (bool, optional): whether password is shown.
                Defaults to False.

        Returns:
            dict: the user data
        """
        return self.coll.find_one(
            {"username": username}, {"password": show_password}
        )

    def authenticate_one_user(self, user_data: dict) -> bool:
        """Authenticate the user, True if it has the correct credentials

        Args:
            user_data (dict): should minimally contains username and password

        Raises:
            ValueError: If username or password is not present,
                or username does not exist
            VerifyMismatchError: If the login is incorrect

        Returns:
            bool: if credential is correct
        """
        # validation of the data
        self.check_missing_fields(user_data, ["username", "password"])
        if not self.is_username_present(user_data["username"]):
            raise ValueError(
                f"Username '{user_data['username']}' does not exists"
            )

        # authenticate user
        hashedpw = self.find_one_user(
            user_data["username"], show_password=True
        )["password"]
        verify_result = self.ph.verify(hashedpw, user_data["password"])

        if self.ph.check_needs_rehash(hashedpw):
            self.coll.delete_one({"username": user_data["username"]})
            self.insert_one_user(user_data)
        return verify_result


userdb = _UserDb(get_mongo_client())
