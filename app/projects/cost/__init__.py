from flask import Blueprint

cost_bp = Blueprint('cost', __name__, template_folder='templates')

from . import routes