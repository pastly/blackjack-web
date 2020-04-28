from flask import Blueprint

bp = Blueprint('time_trial', __name__)

from . import routes  # noqa: W0611
