from flask import flash, redirect, request, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from .forms import LoginForm, RegistrationForm
from . import bp
from .. import db
from ..routes import my_render_template
from ..models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('misc_routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # if no next GET param, or if it exists and is to a different
            # hostname, then default to this page
            next_page = url_for('misc_routes.index')
        return redirect(next_page)
    return my_render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('misc_routes.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('misc_routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have registered! Now login.')
        return redirect(url_for('auth.login'))
    return my_render_template(
        'auth/register.html', title='Register', form=form)
