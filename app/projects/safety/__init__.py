from flask import Blueprint

safety_bp = Blueprint('safety', __name__, template_folder='templates')

from . import routes