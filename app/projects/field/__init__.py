# app/projects/field/__init__.py
from flask import Blueprint

field_bp = Blueprint('field', __name__)

from . import routes