from flask import abort, request
from flask_login import login_required, current_user
from ..routes import my_render_template
from ..models import TimeTrialResult
from .. import db
from . import bp


@bp.route('/')
@login_required
def index():
    return my_render_template('time_trial/index.html', title='Time Trial')


def results_seem_valid(results):
    ''' VERY weak check as this is cbor and I don't want to have to try to
    parse just to send it to the DB '''
    if not len(results):
        return False
    if type(results) != bytes:
        return False
    return True


def try_parse_results(results_dict):
    ''' They come from the user as a dict with key=position and value=byte.
    Just concatenate the bytes together, or return None if we can't
    '''
    # dicts are ordered in python now? Let's make sure that stays the case
    last = -1
    results_bytes = b''
    for k, v in results_dict.items():
        try:
            k = int(k)
        except ValueError:
            return None
        if v < 0 or v > 255:
            return None
        assert k == last + 1
        last += 1
        results_bytes += bytes([v])
    return results_bytes


@bp.route('/results', methods=['POST'])
@login_required
def results():
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    results = try_parse_results(request.json['results'])
    if not results or not results_seem_valid(results):
        abort(400)
    row = TimeTrialResult(
        user_id=current_user.id,
        hands=results,
    )
    db.session.add(row)
    db.session.commit()
    return ('', 204)
