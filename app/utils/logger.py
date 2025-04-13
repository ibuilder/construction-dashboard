import os
import logging
from logging.handlers import RotatingFileHandler
import time
from flask import has_request_context, request

class RequestFormatter(logging.Formatter):
    """Custom formatter that adds request information to log records"""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            if hasattr(request, 'user') and request.user and request.user.is_authenticated:
                record.user_id = request.user.id
            else:
                record.user_id = 'Anonymous'
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.user_id = None
            
        return super().format(record)

def configure_logging(app):
    """Configure logging for the application"""
    
    # Set log level based on configuration
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.root_path, '../logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Set up file handler for all logs
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    
    # Set up file handler for errors only
    error_file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'error.log'),
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    
    # Create formatters
    if app.config.get('ENV') == 'development':
        file_formatter = RequestFormatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(user_id)s - %(remote_addr)s]: %(message)s'
        )
    else:
        file_formatter = RequestFormatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(user_id)s - %(remote_addr)s - %(url)s - %(method)s]: %(message)s'
        )
    
    # Apply formatters
    file_handler.setFormatter(file_formatter)
    error_file_handler.setFormatter(file_formatter)
    
    # Set log level
    file_handler.setLevel(log_level)
    
    # Remove default handlers if they exist
    if app.logger.handlers:
        for handler in app.logger.handlers:
            app.logger.removeHandler(handler)
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.setLevel(log_level)
    
    # Log application startup
    app.logger.info(f"Application startup: {app.config.get('ENV')} environment")