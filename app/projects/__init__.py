from flask import Blueprint

projects_bp = Blueprint('projects', __name__)

from app.projects import routes

# Import all section blueprints
from .preconstruction import preconstruction_bp
from .engineering import engineering_bp
from .field import field_bp
from .safety import safety_bp
from .contracts import contracts_bp
from .cost import cost_bp
from .bim import bim_bp
from .closeout import closeout_bp
from .settings import settings_bp
from .reports import reports_bp

# Register all section blueprints
projects_bp.register_blueprint(preconstruction_bp, url_prefix='/preconstruction')
projects_bp.register_blueprint(engineering_bp, url_prefix='/engineering')
projects_bp.register_blueprint(field_bp, url_prefix='/field')
projects_bp.register_blueprint(safety_bp, url_prefix='/safety')
projects_bp.register_blueprint(contracts_bp, url_prefix='/contracts')
projects_bp.register_blueprint(cost_bp, url_prefix='/cost')
projects_bp.register_blueprint(bim_bp, url_prefix='/bim')
projects_bp.register_blueprint(closeout_bp, url_prefix='/closeout')
projects_bp.register_blueprint(settings_bp, url_prefix='/settings')
projects_bp.register_blueprint(reports_bp, url_prefix='/reports')