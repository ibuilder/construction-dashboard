from flask import Blueprint

preconstruction_bp = Blueprint('preconstruction', __name__, template_folder='templates')

from . import routes, models