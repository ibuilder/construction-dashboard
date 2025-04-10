from flask import Blueprint

bim_bp = Blueprint('bim', __name__, template_folder='templates')

from . import routes