from flask import Blueprint

bp = Blueprint('basic_strategy', __name__)

from . import routes  # noqa: W0611
