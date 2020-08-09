from flask import Blueprint

bp = Blueprint('counting', __name__)

from . import routes  # noqa: W0611
