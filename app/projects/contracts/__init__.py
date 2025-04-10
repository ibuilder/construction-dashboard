from flask import Blueprint

contracts_bp = Blueprint('contracts', __name__, template_folder='templates')

from . import routes