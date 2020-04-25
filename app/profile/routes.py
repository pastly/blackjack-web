from flask import redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from . import bp
from ..models import User
from ..routes import my_render_template


@bp.route('/profile', methods=['GET'])
@login_required
def index():
    if not current_user.is_authenticated:
        # should never happen, right?
        return redirect(url_for('misc_routes.index'))
    return redirect(
        url_for('profile.show',
                id_hash=current_app.hashids.encode(current_user.id)))


@bp.route('/profile/<id_hash>')
def show(id_hash):
    # this returns a tuple
    int_id = current_app.hashids.decode(id_hash)
    # 0 len if invalid hashid, >1 if hashid for a 2+ len tuple
    if len(int_id) != 1:
        abort(404)
    int_id = int_id[0]
    user = User.query.filter_by(id=int_id).first()
    # might have been a valid hashid for a user that doesn't exist
    if not user:
        abort(404)
    return my_render_template(
        'profile/index.html', title=f'{user.username}', user=user)
