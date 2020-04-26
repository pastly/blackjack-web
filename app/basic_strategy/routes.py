import gzip
from flask import abort, request, Response, json
from flask_login import login_required, current_user
from . import bp
from .. import db
from ..routes import my_render_template
from ..models import BasicStrategyPlayStats


@bp.route('/')
def index():
    return my_render_template(
        'basic_strategy/index.html', title='Basic Strategy')


@bp.route('/play-stats/latest')
@login_required
def play_stats_latest():
    BSPS = BasicStrategyPlayStats
    DEFAULT_PLAYSTATS = \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0," + \
        "0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0,0/0"
    DEFAULT_STREAK = 0
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    row = BSPS.query.filter_by(
        user_id=current_user.id).order_by(
            BSPS.time.desc()).first()
    data_bytes = json.dumps(dict(
        play_stats=DEFAULT_PLAYSTATS if not row else
        gzip.decompress(row.play_stats).decode('utf-8'),
        streak=DEFAULT_STREAK if not row else row.streak,
    )).encode('utf-8')
    if 'gzip' in request.accept_encodings:
        resp = Response(gzip.compress(data_bytes))
        resp.headers['Content-Encoding'] = 'gzip'
    else:
        resp = Response(data_bytes)
    resp.headers['Content-Type'] = 'application/json'
    return resp


def play_stats_seem_valid(s):
    # "999/999," 360 times
    MAX_LEN = 360 * 8
    if len(s) > MAX_LEN:
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


@bp.route('/play-stats', methods=['POST'])
@login_required
def play_stats():
    BSPS = BasicStrategyPlayStats
    if not current_user.is_authenticated:
        # should never happen, right?
        abort(403)
    if not play_stats_seem_valid(request.json['play_stats']):
        abort(400)
    play_stats_bytes = request.json['play_stats'].encode('utf-8')
    row = BSPS(
        user_id=current_user.id,
        play_stats=gzip.compress(play_stats_bytes),
        streak=request.json['streak'],
    )
    db.session.add(row)
    db.session.commit()
    return ('', 204)
