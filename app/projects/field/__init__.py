from flask import Blueprint

field_bp = Blueprint('field', __name__, template_folder='templates')

from . import routes