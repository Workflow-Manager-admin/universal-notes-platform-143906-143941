from flask import Flask
from flask_cors import CORS
from .routes.health import blp
from flask_smorest import Api

# Import SQLAlchemy and models
from .models import db

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["API_TITLE"] = "Notes API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Database connection (use SQLite as default; in prod override with env)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///notes.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

api = Api(app)
api.register_blueprint(blp)

# Import and register additional blueprints after app/db/api initialization
from .routes.auth import blp as auth_blp
from .routes.notes import blp as notes_blp
api.register_blueprint(auth_blp)
api.register_blueprint(notes_blp)
