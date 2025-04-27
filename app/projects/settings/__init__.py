# app/projects/settings/__init__.py

from flask import Blueprint

settings_bp = Blueprint('settings', __name__, template_folder='templates')
