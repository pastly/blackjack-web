from flask import Blueprint

bp = Blueprint('deviations', __name__)

from . import routes  # noqa: W0611
