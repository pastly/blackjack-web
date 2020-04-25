from flask import Flask, current_app
from config import Config
from hashids import Hashids
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# For pages that require the user to login, send them to the login page (where
# the string 'login' is what is used in url_for(...) to get the URL)
login.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    app.hashids = Hashids(
        alphabet=app.config['HASHIDS_ALPHABET'],
        min_length=app.config['HASHIDS_MIN_LEN'],
        salt=app.config['HASHIDS_SALT'])

    from app.auth import bp as auth_bp  # noqa: E402
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.profile import bp as profile_bp  # noqa: E402
    app.register_blueprint(profile_bp, url_prefix='/profile')
    from app.basic_strategy import bp as basic_strategy_bp  # noqa: E402
    app.register_blueprint(
        basic_strategy_bp, url_prefix='/train/basic-strategy')
    from app.misc_routes import bp as misc_routes_bp  # noqa: E402
    app.register_blueprint(misc_routes_bp)

    app.add_template_global(name='robohash_url', f=robohash_url)
    app.add_template_global(name='wasm_urls', f=wasm_urls)

    return app


def robohash_url(int_id, size):
    proto = 'https'
    host = 'robohash.org'
    set_ = 'set1'
    hash_id = current_app.hashids.encode(int_id)
    return f'{proto}://{host}/{hash_id}?set={set_}&size={size}x{size}'


def wasm_urls(resource):
    prefix = current_app.config['WASM_URL_PREFIX']
    # return url to the wasm itself and the JS glue for it
    return f'{prefix}/bj_web_{resource}_bg.wasm',\
        f'{prefix}/bj_web_{resource}.js'


from app import routes, models  # noqa: W0611,E402
