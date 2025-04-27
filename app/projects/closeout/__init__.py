# app/projects/closeout/__init__.py
from flask import Blueprint

closeout_bp = Blueprint('projects_closeout', __name__, template_folder='templates')

from . import routes