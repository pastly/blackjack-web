from . import bp
from ..routes import my_render_template


@bp.route('/')
def index():
    return my_render_template('index.html', title='Home')
