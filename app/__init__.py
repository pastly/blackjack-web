from flask import Flask
from config import Config
from hashids import Hashids
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


def robohash_url(int_id, size):
    proto = 'https'
    host = 'robohash.org'
    set_ = 'set1'
    hash_id = hashids.encode(int_id)
    return f'{proto}://{host}/{hash_id}?set={set_}&size={size}x{size}'


def wasm_urls(resource):
    prefix = app.config['WASM_URL_PREFIX']
    # return url to the wasm itself and the JS glue for it
    return f'{prefix}/bj_web_{resource}_bg.wasm',\
        f'{prefix}/bj_web_{resource}.js'


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
hashids = Hashids(
    alphabet=app.config['HASHIDS_ALPHABET'],
    min_length=app.config['HASHIDS_MIN_LEN'],
    salt=app.config['HASHIDS_SALT'])


app.add_template_global(name='robohash_url', f=robohash_url)
app.add_template_global(name='wasm_urls', f=wasm_urls)

# For pages that require the user to login, send them to the login page (where
# the string 'login' is what is used in url_for(...) to get the URL)
login.login_view = 'login'

from app import routes, models  # noqa
