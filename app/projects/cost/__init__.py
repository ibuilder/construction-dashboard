from flask import Blueprint

# Create blueprint with standard naming pattern
bp = Blueprint('cost', __name__)

# Import routes at the end to avoid circular imports
from app.projects.cost import routes