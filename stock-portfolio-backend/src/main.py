import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from server.apis import api_bp
from server.auth.auth_middleware import middleware

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("APP_SECRET_KEY")

app.wsgi_app = middleware(app.wsgi_app)


CORS(app, supports_credentials=True, origin="127.0.0.1")

app.register_blueprint(api_bp)
app.run(host="0.0.0.0", debug=os.getenv("FLASK_ENV", False) == "development")
