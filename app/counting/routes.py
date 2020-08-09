import gzip
import json
from flask import request, Response, abort
from flask_login import login_required, current_user
from . import bp
from ..routes import my_render_template
from ..models import CountingPrefs
from .. import db


DEFAULT_PREFS = {
    'num_decks': 1,
    'num_cards': 52,
    'cards_at_a_time': 1,
    'method': 'interval',
    'interval': 700,
}


@bp.route('/')
@login_required
def index():
    return my_render_template(
        'counting/index.html', title='Card Counting')


def prefs_seem_valid(prefs):
    # All prefs are ints except key="method" at this time, which is a string.
    # So make sure we were given correct things
    for k, v in prefs.items():
        if k == 'method' and isinstance(v, str):
            continue
        elif k != 'method' and isinstance(v, int):
            continue
        else:
            print(k, v)
            return False
    return True


def pref_row_for_user(user_id):
    return CountingPrefs.query.filter_by(user_id=user_id).first()


@bp.route('/prefs', methods=['GET', 'POST'])
@login_required
def prefs():
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    if request.method == 'GET':
        row = pref_row_for_user(current_user.id)
        if not row:
            data_bytes = json.dumps(DEFAULT_PREFS).encode('utf-8')
        else:
            data_bytes = row.prefs
        if 'gzip' in request.accept_encodings:
            resp = Response(gzip.compress(data_bytes))
            resp.headers['Content-Encoding'] = 'gzip'
        else:
            resp = Response(data_bytes)
        resp.headers['Content-Type'] = 'application/json'
        return resp
    assert request.method == 'POST'
    prefs_dict = request.json
    if not prefs_seem_valid(prefs_dict):
        abort(400)
    prefs_bytes = json.dumps(prefs_dict).encode('utf-8')
    existing_row = pref_row_for_user(current_user.id)
    if not existing_row:
        row = CountingPrefs(user_id=current_user.id, prefs=prefs_bytes)
        db.session.add(row)
    else:
        existing_row.prefs = prefs_bytes
        db.session.merge(existing_row)
    db.session.commit()
    return ('', 204)
