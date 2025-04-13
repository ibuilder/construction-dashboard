from flask import Blueprint, g
import time
from app.utils import generate_request_id
from app.config import Config  # In __init__.py

bp = Blueprint('safety', __name__)

@bp.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = generate_request_id()

from app.projects.safety import routes

# First registration
app.register_error_handler(400, handle_400_error)
app.register_error_handler(403, handle_403_error)
app.register_error_handler(404, handle_404_error)
app.register_error_handler(500, handle_500_error)

# Later called again via function
register_error_handlers(app)

# Inside create_app function
scheduler.init_app(app)