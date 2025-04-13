from flask import render_template, jsonify, current_app
import traceback
from werkzeug.exceptions import HTTPException

def handle_400_error(e):
    if request_wants_json():
        return jsonify(error=str(e)), 400
    return render_template('errors/400.html', error=e), 400

def handle_403_error(e):
    if request_wants_json():
        return jsonify(error="Forbidden"), 403
    return render_template('errors/403.html'), 403

def handle_404_error(e):
    if request_wants_json():
        return jsonify(error="Resource not found"), 404
    return render_template('errors/404.html'), 404

def handle_500_error(e):
    # Log the error
    current_app.logger.error(f"Internal server error: {str(e)}")
    current_app.logger.error(traceback.format_exc())
    
    if request_wants_json():
        return jsonify(error="Internal server error"), 500
    return render_template('errors/500.html'), 500

def request_wants_json():
    """Check if the request is expecting JSON response"""
    from flask import request
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (best == 'application/json' and
            request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])