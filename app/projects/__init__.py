# app/projects/__init__.py - Simplified
from flask import Blueprint

# Create main projects blueprint
projects_bp = Blueprint('projects', __name__)

# Import routes to register them with the blueprint
from app.projects.routes import *