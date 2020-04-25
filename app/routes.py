from flask import render_template, flash, redirect, url_for, request, abort,\
    Response
from app import app, db, hashids
from app.forms import LoginForm, RegistrationForm
from app.models import User, BasicStrategyPlayStats
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import gzip


def my_render_template(*a, **kw):
    kw.update({
        'google_analytics_id': app.config['GOOGLE_ANALYTICS'],
    })
    return render_template(*a, **kw)


@app.route('/')
@app.route('/index')
def index():
    return my_render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # if no next GET param, or if it exists and is to a different
            # hostname, then default to this page
            next_page = url_for('index')
        return redirect(next_page)
    return my_render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have registered! Now login.')
        return redirect(url_for('login'))
    return my_render_template('register.html', title='Register', form=form)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    if not current_user.is_authenticated:
        # should never happen, right?
        return redirect(url_for('index'))
    return redirect(
        url_for('profile_show', id_hash=hashids.encode(current_user.id)))
    # return my_render_template('profile.html', title='Profile')


@app.route('/profile/<id_hash>')
def profile_show(id_hash):
    # this returns a tuple
    int_id = hashids.decode(id_hash)
    # 0 len if invalid hashid, >1 if hashid for a 2+ len tuple
    if len(int_id) != 1:
        abort(404)
    int_id = int_id[0]
    user = User.query.filter_by(id=int_id).first()
    # might have been a valid hashid for a user that doesn't exist
    if not user:
        abort(404)
    return my_render_template(
        'profile.html', title=f'{user.username}', user=user)


@app.route('/train/basic-strategy')
def train_basic_strategy():
    return my_render_template(
        'train-basic-strategy.html', title='Basic Strategy')


@app.route('/train/basic-strategy/play-stats/latest')
@login_required
def train_basic_strategy_play_stats_latest():
    BSPS = BasicStrategyPlayStats
    DEFAULT = gzip.compress(
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," +
        b"0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0")
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    stats = BSPS.query.filter_by(
        user_id=current_user.id).order_by(
            BSPS.time.desc()).first()
    data = DEFAULT if not stats else stats.data
    if 'gzip' not in request.accept_encodings:
        resp = Response(gzip.decompress(data))
    else:
        resp = Response(data)
        resp.headers['Content-Encoding'] = 'gzip'
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/train/basic-strategy/play-stats', methods=['POST'])
@login_required
def train_basic_strategy_play_stats():
    def seems_valid(s_bytes):
        # "999/999," 360 times
        MAX_LEN = 360 * 8
        if len(s_bytes) > MAX_LEN:
            return False
        try:
            s = s_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return False
        # must have 360 items
        parts = s.split(',')
        if len(parts) != 360:
            return False
        for part in parts:
            # each must look like a fraction
            sub_parts = part.split('/')
            if len(sub_parts) != 2:
                return False
            try:
                # with valid ints
                n, d = [int(_) for _ in sub_parts]
            except ValueError:
                return False
            # and numerator can't be bigger than denominator
            if n > d:
                return False
        return True
    BSPS = BasicStrategyPlayStats
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    if not seems_valid(request.data):
        abort(400)
    row = BSPS(user_id=current_user.id, data=gzip.compress(request.data))
    db.session.add(row)
    db.session.commit()
    return ('', 204)
