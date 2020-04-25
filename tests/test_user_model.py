from unittest import TestCase
from pytest import raises
from sqlalchemy.exc import IntegrityError
from . import TestConfig
from app import create_app, db
from app.models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_empty_create(self):
        u = User()
        db.session.add(u)
        with raises(IntegrityError):
            db.session.commit()

    def test_no_username_create(self):
        u = User(email='foo@example.com')
        u.set_password('bar')
        db.session.add(u)
        with raises(IntegrityError):
            db.session.commit()

    def test_no_email_create(self):
        u = User(username='foo')
        u.set_password('bar')
        db.session.add(u)
        with raises(IntegrityError):
            db.session.commit()

    def test_no_password_create(self):
        u = User(username='foo', email='foo@example.com')
        db.session.add(u)
        with raises(IntegrityError):
            db.session.commit()

    def test_good(self):
        # can put it in db
        u = User(username='foo', email='foo@example.com')
        u.set_password('bar')
        db.session.add(u)
        db.session.commit()
        users = User.query.all()
        assert len(users) == 1
        # can get it back out
        u = User.query.first()
        assert u.username == 'foo'
        assert u.email == 'foo@example.com'
        assert u.check_password('bar')
