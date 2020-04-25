from flask import Blueprint

bp = Blueprint('misc_routes', __name__)

from . import routes  # noqa: W0611
