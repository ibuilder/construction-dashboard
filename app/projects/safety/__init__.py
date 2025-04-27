# app/projects/safety/__init__.py
from flask import Blueprint, g
import time
from app.utils import generate_request_id
from app.config import Config

bp = Blueprint('safety', __name__)

@bp.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = generate_request_id()

from app.projects.safety import routes