from flask_login import login_required
from . import bp
from ..routes import my_render_template


@bp.route('/')
@login_required
def index():
    return my_render_template(
        'deviations/index.html', title='Deviations')
