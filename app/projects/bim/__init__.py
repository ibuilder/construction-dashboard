from flask import Blueprint

# Create blueprint with a simple name - parent relationships are handled during registration
bp = Blueprint('bim', __name__)

# Import routes at the end to avoid circular imports
from app.projects.bim import routes