from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, jsonify, make_response, request
from server.auth.session_manager import SessionManager
from server.database.userdb import userdb

user_api_bp = Blueprint("user", __name__, url_prefix="user")

session_manager = SessionManager()


@user_api_bp.get("")
def user_session_available():
    """Check if user session is available

    Json Response:
        + 200 {"isLogin": bool}
    """
    return jsonify(
        {"isLogin": request.environ.get("sessionid") in session_manager}
    )


@user_api_bp.post("")
def user_login():
    """Logins the user

    Requires:
        json: {"username", "password"}

    Json Response:
        + 200 {"sessionid": str}
        + 401 {"error", "Incorrect Login Credentials"}
    """

    user_data = request.json
    try:
        if userdb.authenticate_one_user(user_data):
            result = userdb.find_one_user(user_data["username"])
            session_id = session_manager.new_user_ses(str(result["_id"]))
            result.pop("_id")
            response = make_response(jsonify(result), 200)
            response.set_cookie(
                "sessionid", session_id, path="/", samesite="Lax", httponly=True
            )
            return response
        else:
            raise VerifyMismatchError("Incorrect Login Credentials")

    except (ValueError, VerifyMismatchError) as e:
        print(e)
        return jsonify({"error": "Incorrect Login Credentials"}), 401


@user_api_bp.get("/logout")
def user_logout():
    """Logout the user

    Requires:
        valid request cookies containing key "sessionid"

    Json Response:
        + 200 {"ok": True}
    """
    session_manager.remove_ses(request.cookies.get("sessionid", ""))
    response = make_response(jsonify({"ok": True}), 200)
    response.delete_cookie("sessionid", path="/")
    return response


@user_api_bp.put("")
def user_signup():
    """Create new user account

    Requires:
        json: {"username", "password", "name"}

    Json Response:
        + 200 {"sessionid": str session_id}
        + 406 {"error": str error_msg}
    """

    user_data = request.json
    try:
        userid = userdb.insert_one_user(user_data)
    except ValueError as e:
        print(e)
        return jsonify({"error": str(e)}), 406

    return jsonify({"sessionid": session_manager.new_user_ses(userid)}), 200
