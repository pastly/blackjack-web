from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
import gzip

# https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
# https://docs.sqlalchemy.org/en/13/core/compiler.html#utc-timestamp-function
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime, TypeDecorator


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'sqlite')
def sqlite_utcnow(element, compiler, **kw):
    return 'CURRENT_TIMESTAMP'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GzippedString(TypeDecorator):
    ''' Take a str ('' not b'') and gzip before putting in DB and ungzip before
    pulling from DB
    '''

    impl = db.LargeBinary

    def process_bind_param(self, value, dialect):
        return gzip.compress(value.encode('utf-8'))

    def process_result_value(self, value, dialect):
        return gzip.decompress(value).decode('utf-8')


class GzippedBytes(TypeDecorator):
    ''' Take bytes (b'' not '') and gzip before putting in DB and ungzip before
    pulling from DB
    '''

    impl = db.LargeBinary

    def process_bind_param(self, value, dialect):
        return gzip.compress(value)

    def process_result_value(self, value, dialect):
        return gzip.decompress(value)


class BasicStrategyPlayStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=utcnow(), nullable=False)
    play_stats = db.Column(GzippedString(length=1024), nullable=False)
    streak = db.Column(db.Integer, nullable=False)


class TimeTrialResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=utcnow(), nullable=False)
    hands = db.Column(GzippedBytes(length=25*1024), nullable=False)


class CountingPrefs(db.Model):
    user_id = db.Column(
        db.ForeignKey('user.id'), nullable=False, primary_key=True)
    prefs = db.Column(GzippedBytes(length=1*1024), nullable=False)
