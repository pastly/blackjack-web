from . import bp
from ..routes import my_render_template


@bp.route('/')
def index():
    return my_render_template('index.html', title='Home')

@bp.route('/faq')
def faq():
    return my_render_template('faq.html', title='FAQ')
