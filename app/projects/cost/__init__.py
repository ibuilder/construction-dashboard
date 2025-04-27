# app/projects/cost/__init__.py
from flask import Blueprint

cost_bp = Blueprint('cost', __name__, url_prefix='/projects/cost')

# Import routes after creating the blueprint
from app.projects.cost import routes