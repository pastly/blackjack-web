from flask import Blueprint

bp = Blueprint('auth', __name__)

from . import routes, forms  # noqa: W0611
