# app/projects/engineering/__init__.py
from flask import Blueprint

engineering_bp = Blueprint('engineering', __name__)

from . import routes