from flask import Flask, request, g, jsonify
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf, mail, moment, cache, limiter, monitor, scheduler
from app.utils.security import configure_security
import os
import logging
from logging.handlers import RotatingFileHandler
import time

# Define Swagger URL constant
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI

def create_app(config_class=None):
    if config_class is None:
        from app.config_factory import get_config
        config_class = get_config()
        
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    
    # Configure caching
    cache_config = {
        'CACHE_TYPE': 'simple',  # Use FileSystemCache or RedisCache in production
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)
    
    # Initialize rate limiting
    limiter.init_app(app)
    
    # Initialize monitoring
    monitor.init_app(app)
    
    # Initialize task scheduler
    scheduler.init_app(app)
    
    # Configure security middleware
    configure_security(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register request timing and monitoring middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = generate_request_id()
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log slow requests
            if duration > app.config.get('SLOW_REQUEST_THRESHOLD', 0.5):
                app.logger.warning(f"Slow request: {request.method} {request.path} - {duration:.4f}s")
            
            # Record in monitoring
            endpoint = request.endpoint or 'unknown'
            monitor.record_request(endpoint, request.method, response.status_code, duration)
            
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Register error tracking
    @app.errorhandler(Exception)
    def handle_exception(e):
        monitor.record_error(e, request.endpoint, request.method, request.path)
        # Continue with normal error handling
        raise e
    
    # Register blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.projects import projects_bp
    from app.admin import admin_bp
    from app.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.api.swagger import swagger_bp, swagger_ui_bp
    app.register_blueprint(swagger_bp, url_prefix='/api')
    app.register_blueprint(swagger_ui_bp, url_prefix=SWAGGER_URL)
    
    # Register error handlers
    from app.utils.error_handlers import (
        handle_400_error, handle_403_error, 
        handle_404_error, handle_500_error
    )
    
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    
    # Create context processor to make global variables available in templates
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            'current_year': datetime.now().year,
            'app_name': app.config.get('COMPANY_NAME', 'Construction Dashboard'),
            'app_version': '1.0.0'
        }
    
    # Add utility context processor
    @app.context_processor
    def utility_processor():
        def format_currency(value):
            return "${:,.2f}".format(value) if value else "$0.00"
        
        def format_date(value, format='%m/%d/%Y'):
            if not value:
                return ""
            return value.strftime(format)
            
        def format_filesize(bytes):
            """Convert bytes to human-readable form"""
            if not bytes:
                return "0B"
            units = ['B', 'KB', 'MB', 'GB']
            i = 0
            while bytes >= 1024 and i < len(units) - 1:
                bytes /= 1024
                i += 1
            return f"{bytes:.2f} {units[i]}"
            
        return dict(
            format_currency=format_currency,
            format_date=format_date,
            format_filesize=format_filesize
        )
    
    # Add request timing
    @app.before_request
    def before_request():
        g.start = time.time()
        g.request_id = generate_request_id()
    
    @app.after_request
    def after_request(response):
        # Log request timing
        if hasattr(g, 'start'):
            diff = time.time() - g.start
            if app.debug or diff > 1.0:  # Log all in debug mode, or slow requests in production
                app.logger.info(f"Request {g.request_id}: {request.method} {request.path} - {diff:.4f}s")
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Create health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        health_data = {
            'status': 'ok',
            'timestamp': time.time(),
            'version': '1.0.0',
            'database': check_db_connection()
        }
        
        status_code = 200 if health_data['database'] else 503
        return jsonify(health_data), status_code
    
    # Exempt API routes from CSRF protection
    exempt_csrf_for_api_routes(app)
    
    # Configure logging
    from app.utils.logger import configure_logging
    configure_logging(app)
    
    # Register shell context processor
    register_shell_context(app)
    
    # Run startup tasks
    run_startup_tasks(app)
    
    # Add security middleware
    from app.utils.security import add_security_headers
    app.after_request(add_security_headers)
    
    return app

def generate_request_id():
    """Generate a unique ID for the current request"""
    import uuid
    return str(uuid.uuid4())

def register_shell_context(app):
    """Register shell context objects"""
    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User
        from app.models.project import Project
        from app.models.engineering import RFI, Submittal
        from app.models.field import DailyReport
        from app.models.safety import SafetyObservation, IncidentReport
        from app.models.cost import Budget, ChangeOrder, Invoice
        
        return {
            'db': db,
            'User': User,
            'Project': Project,
            'RFI': RFI,
            'Submittal': Submittal,
            'DailyReport': DailyReport,
            'SafetyObservation': SafetyObservation,
            'IncidentReport': IncidentReport,
            'Budget': Budget,
            'ChangeOrder': ChangeOrder,
            'Invoice': Invoice
        }

def check_db_connection():
    """Check database connection"""
    try:
        result = db.session.execute('SELECT 1').scalar()
        return result == 1
    except Exception as e:
        current_app.logger.error(f"Database connection failed: {str(e)}")
        return False

def exempt_csrf_for_api_routes(app):
    """Exempt API routes from CSRF protection"""
    # Get CSRF protection instance
    csrf_protect = csrf._csrf
    
    # Configure exempt routes
    @csrf_protect.exempt
    def csrf_exempt_api():
        if request.path.startswith('/api/'):
            return True
        return False

def run_startup_tasks(app):
    """Run tasks at application startup"""
    with app.app_context():
        # Check and create required database tables
        if app.config.get('AUTO_MIGRATE', False):
            try:
                db.create_all()
                app.logger.info('Database tables created')
            except Exception as e:
                app.logger.error(f'Error creating database tables: {e}')
        
        # Check and create required directories
        required_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'temp'),
            'logs'
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                app.logger.info(f'Created directory: {directory}')
        
        # Check feature flags
        try:
            from app.utils.feature_flags import load_feature_flags
            load_feature_flags()
            app.logger.info('Feature flags loaded')
        except ImportError:
            app.logger.info('Feature flags module not found, skipping')
        
        # Register maintenance tasks
        from app.utils.scheduler import clean_temp_files
        
        # Add scheduled tasks
        scheduler.add_daily_task(lambda: clean_temp_files(app), "03:00", "temp_file_cleanup")
        
        # Add database stats collection (every 6 hours)
        def collect_db_stats():
            try:
                active_users = db.session.execute("SELECT COUNT(*) FROM users WHERE last_seen > NOW() - INTERVAL '24 hours'").scalar()
                app.logger.info(f"Daily active users: {active_users}")
            except Exception as e:
                app.logger.error(f"Error collecting DB stats: {str(e)}")
                
        scheduler.add_task(collect_db_stats, 60*60*6, "db_stats_collection")
        
        # Start the scheduler if we're not in testing mode
        if not app.testing:
            scheduler.start()

    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    from app.utils.error_handlers import (
        handle_400_error,
        handle_403_error,
        handle_404_error,
        handle_500_error
    )
    
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)