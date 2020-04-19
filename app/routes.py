from flask import render_template, flash, redirect, url_for, request, abort
from app import app, db, hashids
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


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


@app.route('/private')
@login_required
def private():
    if not current_user.is_authenticated:
        return 'Somehow an unauthenticated user got to here :('
    return 'This is a private page'


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
