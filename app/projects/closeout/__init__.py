from flask import Blueprint

closeout_bp = Blueprint('closeout', __name__, template_folder='templates')

from . import routes