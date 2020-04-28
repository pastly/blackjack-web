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


class PlayStats(TypeDecorator):
    ''' Gzips the string representation of Table<PlayStats> before storing in
    DB, and un-gzips when pulling it out.
    '''

    impl = db.LargeBinary

    def process_bind_param(self, value, dialect):
        return gzip.compress(value.encode('utf-8'))

    def process_result_value(self, value, dialect):
        return gzip.decompress(value).decode('utf-8')


class BasicStrategyPlayStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.DateTime, server_default=utcnow(), nullable=False)
    play_stats = db.Column(PlayStats(length=1024), nullable=False)
    streak = db.Column(db.Integer, nullable=False)
