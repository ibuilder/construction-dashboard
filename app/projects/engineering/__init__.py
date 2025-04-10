from flask import Blueprint

engineering_bp = Blueprint('engineering', __name__, template_folder='templates')

from . import routes