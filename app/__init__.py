from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# For pages that require the user to login, send them to the login page (where
# the string 'login' is what is used in url_for(...) to get the URL)
login.login_view = 'login'

from app import routes, models  # noqa
