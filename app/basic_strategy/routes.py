import gzip
from flask import abort, request, Response, current_app
from flask_login import login_required, current_user
from . import bp
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


@bp.route('/play-stats', methods=['POST'])
@login_required
def play_stats():
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
    current_app.db.session.add(row)
    current_app.db.session.commit()
    return ('', 204)
