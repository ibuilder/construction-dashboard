from flask import request, g, current_app, abort
from werkzeug.exceptions import Forbidden
import re
import ipaddress
from functools import wraps
import html

def configure_security(app):
    """Configure security middlewares and settings"""
    
    @app.before_request
    def validate_request():
        """Validate request for security purposes"""
        # Block potentially dangerous file uploads
        if request.method == "POST" and request.files:
            for file in request.files.values():
                filename = file.filename
                if filename and not allowed_file(filename):
                    current_app.logger.warning(f"Blocked upload of potentially dangerous file: {filename}")
                    return "File type not allowed", 400
        
        # Check for common SQL injection patterns
        if has_sql_injection(request):
            current_app.logger.warning(f"Potential SQL injection attempt from {request.remote_addr}")
            return "Access denied", 403

        # Check cross-site request forgery for non-API endpoints
        if not request.path.startswith('/api/') and request.method not in ['GET', 'HEAD', 'OPTIONS']:
            csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not csrf_token:
                current_app.logger.warning(f"Missing CSRF token in request from {request.remote_addr}")
                return "CSRF token missing", 403
            
        # IP address allowlist for admin routes (if configured)
        if request.path.startswith('/admin/') and app.config.get('ADMIN_IP_ALLOWLIST'):
            client_ip = get_client_ip()
            if not is_ip_allowed(client_ip, app.config.get('ADMIN_IP_ALLOWLIST')):
                current_app.logger.warning(f"Admin access attempt from unauthorized IP: {client_ip}")
                return "Access denied", 403

    @app.after_request
    def add_security_headers(response):
        """Add security headers to response"""
        
        # Get CSP settings from config
        csp_settings = current_app.config.get('CSP_SETTINGS', {})
        
        # Build CSP header value
        csp_parts = []
        for directive, sources in csp_settings.items():
            if sources:  # Skip empty sources
                source_string = ' '.join(sources)
                csp_parts.append(f"{directive} {source_string}")
            else:  # Handle directives with no sources (like upgrade-insecure-requests)
                csp_parts.append(directive)
        
        if csp_parts:
            response.headers['Content-Security-Policy'] = '; '.join(csp_parts)
        
        # Add other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add HSTS header in production
        if current_app.config.get('ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

def allowed_file(filename):
    """Check if the file type is allowed"""
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'rtf',
        'jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp',
        'zip', 'tar', 'gz', 'rar'
    }
    
    # Block potentially dangerous file types that could be executed
    BLOCKED_EXTENSIONS = {
        'exe', 'sh', 'bat', 'cmd', 'com', 'dll', 'msi',
        'js', 'php', 'py', 'pl', 'rb', 'asp', 'aspx', 'jsp',
        'html', 'htm', 'xhtml', 'phtml'
    }
    
    if '.' not in filename:
        return False
        
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext in BLOCKED_EXTENSIONS:
        return False
        
    return ext in ALLOWED_EXTENSIONS

def sanitize_input(input_string):
    """
    Sanitize input to prevent XSS and SQL injection
    
    :param input_string: Input string to sanitize
    :return: Sanitized string
    """
    if not isinstance(input_string, str):
        return input_string
    
    # HTML escape
    input_string = html.escape(input_string)
    
    # Remove potential SQL injection patterns
    input_string = re.sub(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)', '', input_string, flags=re.IGNORECASE)
    
    return input_string

def has_sql_injection(req):
    """
    Check for potential SQL injection in request
    
    :param req: Flask request object
    :return: Boolean indicating potential SQL injection
    """
    # Skip SQL injection check for certain routes or methods
    if req.method in ['GET', 'HEAD', 'OPTIONS']:
        return False
    
    # Check query parameters
    for key, value in req.args.items():
        if contains_sql_injection(str(value)):
            return True
    
    # Check form data
    if req.form:
        for key, value in req.form.items():
            if contains_sql_injection(str(value)):
                return True
    
    # Check JSON data with safe handling
    try:
        if req.is_json:
            json_data = req.get_json(silent=True)
            if json_data:
                for key, value in json_data.items():
                    if contains_sql_injection(str(value)):
                        return True
    except Exception:
        # Silently handle JSON parsing errors
        pass
    
    return False


def contains_sql_injection(input_string):
    """
    Detect potential SQL injection patterns
    
    :param input_string: String to check
    :return: Boolean indicating potential SQL injection
    """
    if not isinstance(input_string, str):
        return False
    
    # SQL injection patterns
    sql_injection_patterns = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b',  # SQL keywords
        r'--',  # SQL comment
        r"['\"]\s*OR\s*1\s*=\s*1",  # Classic OR 1=1 injection
        r"['\"]\s*;",  # Potential statement termination
        r'\bOR\b',  # Potential boolean-based injection
        r"['\"]\s*AND\s*['\"0-9a-zA-Z]+\s*=\s*['\"0-9a-zA-Z]",  # AND-based injection
        r"(\/\*.*\*\/)",  # Block comments
    ]
    
    # Convert to lowercase for case-insensitive matching
    input_lower = input_string.lower()
    
    # Check against injection patterns
    for pattern in sql_injection_patterns:
        if re.search(pattern, input_lower):
            return True
    
    return False

def validate_request():
    """
    Middleware to validate incoming requests
    """
    # Skip validation for certain routes if needed
    if request.path.startswith('/static/') or request.path.startswith('/favicon.ico'):
        return
    
    # Check for SQL injection
    if has_sql_injection(request):
        # Log the potential attack
        app.logger.warning(f"Potential SQL injection attempt from {request.remote_addr}")
        # You might want to add more sophisticated handling here
        # For now, we'll just prevent further processing
        abort(400, description="Invalid request")
def validate_input(func):
    """Decorator to validate input parameters for SQL injection"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Define patterns for potentially malicious input
        sql_injection_pattern = re.compile(r'((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))', re.IGNORECASE)
        
        # Check all request args
        for key, value in request.args.items():
            if isinstance(value, str) and sql_injection_pattern.search(value):
                current_app.logger.warning(f"Potential SQL injection attempt detected in request args: {key}={value}")
                abort(400, "Invalid request parameters")
        
        # Check all form data
        for key, value in request.form.items():
            if isinstance(value, str) and sql_injection_pattern.search(value):
                current_app.logger.warning(f"Potential SQL injection attempt detected in form data: {key}={value}")
                abort(400, "Invalid form data")
        
        return func(*args, **kwargs)
    return decorated_function

def get_client_ip():
    """Get client IP address, respecting proxies"""
    if 'X-Forwarded-For' in request.headers:
        # If behind proxy, get real IP
        forwarded_for = request.headers.getlist("X-Forwarded-For")[0]
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr

def is_ip_allowed(ip, allowed_ips):
    """Check if IP is in allowed list (supports CIDR notation)"""
    if not ip:
        return False
        
    try:
        client_ip = ipaddress.ip_address(ip)
        
        for allowed in allowed_ips:
            # Check if allowed is a CIDR range or single IP
            if '/' in allowed:
                network = ipaddress.ip_network(allowed, strict=False)
                if client_ip in network:
                    return True
            else:
                if ip == allowed:
                    return True
    except ValueError:
        current_app.logger.error(f"Invalid IP address in check: {ip}")
        return False
        
    return False

def add_security_headers(response):
    """Add security headers to the response"""
    if not hasattr(current_app, 'config'):
        return response
        
    # Get secure headers from config
    secure_headers = current_app.config.get('SECURE_HEADERS', {})
    
    # Add headers if not already present
    for header, value in secure_headers.items():
        if header not in response.headers:
            response.headers[header] = value
    
    return response