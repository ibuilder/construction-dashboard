# app/projects/overview/__init__.py
from flask import Blueprint

overview_bp = Blueprint('overview', __name__)

from . import routes