from flask import request, g, current_app
from werkzeug.exceptions import Forbidden
import re
import ipaddress

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
        """Add security headers to all responses"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        # Adjust as needed for your application
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'", 
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'self'",
            "form-action 'self'",
        ]
        
        response.headers['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Only send cookies over HTTPS in production
        if not current_app.debug and not current_app.testing:
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

def has_sql_injection(request):
    """Check for common SQL injection patterns"""
    # Simple SQL injection patterns
    patterns = [
        r"'(?:\s+)?--",
        r';(?:\s+)?--',
        r'OR\s+1\s*=\s*1',
        r'DROP\s+TABLE',
        r'INSERT\s+INTO',
        r'DELETE\s+FROM',
        r'UNION\s+SELECT',
        r'EXEC\s+xp_',
        r'WAITFOR\s+DELAY'
    ]
    
    # Check query parameters and form data
    params = []
    if request.args:
        params.extend(request.args.values())
    if request.form:
        params.extend(request.form.values())
    if request.json:
        params.extend([str(v) for v in request.json.values()])
    
    # Check each parameter against patterns
    for param in params:
        if not isinstance(param, str):
            continue
        for pattern in patterns:
            if re.search(pattern, param, re.IGNORECASE):
                return True
    
    return False

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