# app/projects/preconstruction/__init__.py
from flask import Blueprint

preconstruction_bp = Blueprint('projects_preconstruction', __name__, template_folder='templates')

from . import routes