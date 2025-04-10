from flask import Blueprint

web3_bp = Blueprint('web3', __name__)

from . import contracts  # Import contracts to ensure they are registered with the blueprint