from flask_login import login_required
from ..routes import my_render_template
from . import bp


@bp.route('/')
@login_required
def index():
    return my_render_template('time_trial/index.html', title='Time Trial')
