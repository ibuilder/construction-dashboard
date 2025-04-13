from flask import Blueprint

# Create main projects blueprint
projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

# Import sub-blueprints
from app.projects.bim import bp as bim_bp
from app.projects.closeout import bp as closeout_bp
from app.projects.contracts import bp as contracts_bp
from app.projects.cost import bp as cost_bp
from app.projects.engineering import bp as engineering_bp
from app.projects.field import bp as field_bp
from app.projects.preconstruction import bp as preconstruction_bp
from app.projects.reports import bp as reports_bp
from app.projects.safety import bp as safety_bp
from app.projects.settings import bp as settings_bp

# Register sub-blueprints with consistent URL structure
projects_bp.register_blueprint(bim_bp, url_prefix='/<int:project_id>/bim')
projects_bp.register_blueprint(closeout_bp, url_prefix='/<int:project_id>/closeout')
projects_bp.register_blueprint(contracts_bp, url_prefix='/<int:project_id>/contracts')
projects_bp.register_blueprint(cost_bp, url_prefix='/<int:project_id>/cost')
projects_bp.register_blueprint(engineering_bp, url_prefix='/<int:project_id>/engineering')
projects_bp.register_blueprint(field_bp, url_prefix='/<int:project_id>/field')
projects_bp.register_blueprint(preconstruction_bp, url_prefix='/<int:project_id>/preconstruction')
projects_bp.register_blueprint(reports_bp, url_prefix='/<int:project_id>/reports')
projects_bp.register_blueprint(safety_bp, url_prefix='/<int:project_id>/safety')
projects_bp.register_blueprint(settings_bp, url_prefix='/<int:project_id>/settings')

