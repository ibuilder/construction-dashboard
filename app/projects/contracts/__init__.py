# File: construction-dashboard/app/projects/contracts/__init__.py
from flask import Blueprint

contracts_bp = Blueprint('contracts', __name__, template_folder='templates')

from . import routes