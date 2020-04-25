from unittest import TestCase
from . import TestConfig
from app import create_app, db
from app.models import User, BasicStrategyPlayStats
from app.basic_strategy.routes import play_stats_seem_valid
from flask import url_for
import gzip

USER_NAME = 'alice'
USER_EMAIL = 'alice@example.com'
USER_PASS = 'alice'


class BasicStrategyTests(TestCase):
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

    def insert_playstats(self, user):
        data = b'1/2,' * 360
        data = data[:len(data)-1]  # remove trailing comma
        ps = BasicStrategyPlayStats(user_id=user.id, data=gzip.compress(data))
        db.session.add(ps)
        db.session.commit()
        return ps

    def login(self):
        resp = self.client.post(url_for('auth.login'), data=dict(
            username=USER_NAME,
            password=USER_PASS,
        ), follow_redirects=True)
        return resp

    def test_latest_anonymous(self):
        # trying to fetch latest play stats while not being logged in results
        # in redirect to log in
        this = url_for('basic_strategy.play_stats_latest')
        resp = self.client.get(this)
        assert resp.status_code == 302
        loc = resp.headers['Location']
        exp = url_for('auth.login', next=this)
        assert loc.endswith(exp)

    def test_latest_empty(self):
        # when no latest, receive default all-zero data
        self.create_user()
        self.login()
        this = url_for('basic_strategy.play_stats_latest')
        resp = self.client.get(this)
        assert resp.status_code == 200
        # Borrow the real validator to make sure it's valid
        # TODO maybe validate it ourself?
        assert play_stats_seem_valid(resp.data)
        # Make sure it's all zeros by removing zeros and the puncuation and
        # verifying nothing is left. Wow such hacky
        s = resp.data.decode('utf-8')
        assert not len(s.replace('0', '').replace('/', '').replace(',', ''))

    def test_latest_empty_gzip(self):
        # when no latest, receive default all-zero data
        self.create_user()
        self.login()
        this = url_for('basic_strategy.play_stats_latest')
        resp = self.client.get(
            this, headers=[('Accept-Encoding', 'gzip')])
        assert resp.status_code == 200
        assert resp.headers['Content-Encoding'] == 'gzip'
        data = gzip.decompress(resp.data)
        # Borrow the real validator to make sure it's valid
        # TODO maybe validate it ourself?
        assert play_stats_seem_valid(data)
        # Make sure it's all zeros by removing zeros and the puncuation and
        # verifying nothing is left. Wow such hacky
        s = data.decode('utf-8')
        assert not len(s.replace('0', '').replace('/', '').replace(',', ''))

    def test_latest(self):
        # latest exists, and isn't all zero
        u = self.create_user()
        self.login()
        self.insert_playstats(u)
        this = url_for('basic_strategy.play_stats_latest')
        resp = self.client.get(this)
        assert resp.status_code == 200
        # Borrow the real validator to make sure it's valid
        # TODO maybe validate it ourself?
        assert play_stats_seem_valid(resp.data)
        # Make sure it's NOT all zeros by removing zeros and the puncuation and
        # verifying something is left. Wow such hacky.
        s = resp.data.decode('utf-8')
        assert len(s.replace('0', '').replace('/', '').replace(',', ''))

    def test_latest_gzip(self):
        # latest exists, and isn't all zero
        u = self.create_user()
        self.login()
        self.insert_playstats(u)
        this = url_for('basic_strategy.play_stats_latest')
        resp = self.client.get(
            this, headers=[('Accept-Encoding', 'gzip')])
        assert resp.status_code == 200
        assert resp.headers['Content-Encoding'] == 'gzip'
        data = gzip.decompress(resp.data)
        # Borrow the real validator to make sure it's valid
        # TODO maybe validate it ourself?
        assert play_stats_seem_valid(data)
        # Make sure it's NOT all zeros by removing zeros and the puncuation and
        # verifying something is left. Wow such hacky.
        s = data.decode('utf-8')
        assert len(s.replace('0', '').replace('/', '').replace(',', ''))

    def test_post_playstats_anonymous(self):
        this = url_for('basic_strategy.play_stats')
        resp = self.client.post(this)
        assert resp.status_code == 302
        loc = resp.headers['Location']
        exp = url_for('auth.login', next=this)
        assert loc.endswith(exp)

    def test_post_playstats_authenticated_invalid(self):
        self.create_user()
        self.login()
        this = url_for('basic_strategy.play_stats')
        for data in [
            b'',
            b'9287984234',
            b'0/0,0/0',  # too short
            b'0/0,' * 360,  # trailing comma
            (b'0/0,' * 360) + b'0/0',  # too long
            (b'2/1,' * 359) + b'1/2',  # numerator bigger than denominator
                ]:
            resp = self.client.post(this, content_type='text/plain', data=data)
            assert resp.status_code == 400

    def test_post_playstats_authenticated(self):
        self.create_user()
        self.login()
        this = url_for('basic_strategy.play_stats')
        data_in = b'1/2,' * 359 + b'1/2'
        resp = self.client.post(this, content_type='text/plain', data=data_in)
        # data posts correctly
        assert resp.status_code == 204
        # it made it to the database
        rows = BasicStrategyPlayStats.query.all()
        assert len(rows) == 1
        row = rows[0]
        # the database has the correct data
        data_out = gzip.decompress(row.data)
        assert data_in == data_out
