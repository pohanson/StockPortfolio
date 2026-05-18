import json

from werkzeug.wrappers import Request, Response

from server.auth.session_manager import SessionManager


class middleware:
    session_manager = SessionManager()  # sessionid: userid

    def __init__(self, app) -> None:
        self.app = app

    def __call__(self, environ, start_response):

        request = Request(environ)
        sessionid = request.cookies.get("sessionid")

        # ignore url that deals with user signup, login, and logout
        whitelist = ["/api/v0/user", "/api/v1/user"]

        # invalid id or not found means not valid user if not whitelisted url
        if request.path not in whitelist and (
            sessionid is None or sessionid not in self.session_manager
        ):
            res = Response(
                json.dumps({"error": "Authorisation Failed"}),
                mimetype="application/json",
                status=401,
            )
            return res(environ, start_response)

        environ.update(userid=self.session_manager.get_ses_user(sessionid))
        environ.update(sessionid=sessionid)

        print(
            f"sessionid:\t{sessionid}", f"\nuserid:  \t{environ.get('userid')}"
        )
        return self.app(environ, start_response)
