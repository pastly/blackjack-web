from unittest import TestCase
from . import TestConfig
from app import create_app, db
from app.models import User
from flask import url_for

USER_NAME = 'alice'
USER_EMAIL = 'alice@example.com'
USER_PASS = 'alice'


class ProfileTests(TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.request_context.pop()

    def create_user(self):
        u = User(username=USER_NAME, email=USER_EMAIL)
        u.set_password(USER_PASS)
        db.session.add(u)
        db.session.commit()
        return u

    def login(self):
        resp = self.client.post(url_for('auth.login'), data=dict(
            username=USER_NAME,
            password=USER_PASS,
        ), follow_redirects=True)
        return resp

    def test_index_anonymous(self):
        # not logged in means redirect to login page
        resp = self.client.get(url_for('profile.index'))
        assert resp.status_code == 302
        location = resp.headers['Location']
        expected = url_for('auth.login', next=url_for('profile.index'))
        print(location)
        print(expected)
        assert location.endswith(expected)

    def test_index_authenticated(self):
        # logged in, redirect to proper profile page
        user = self.create_user()
        self.login()
        resp = self.client.get(url_for('profile.index'))
        assert resp.status_code == 302
        location = resp.headers['Location']
        expected = url_for(
            'profile.show', id_hash=self.app.hashids.encode(user.id))
        assert location.endswith(expected)
