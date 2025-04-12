## Utility Files

### Access Control
from functools import wraps
from flask import flash, redirect, url_for, abort, request, current_app
from flask_login import current_user

def role_required(roles):
    """
    Decorator for views that checks if the logged in user has the required role
    :param roles: List of roles that can access the route
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles and 'Admin' not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def project_access_required(f):
    """
    Decorator to check if the current user has access to the project.
    Must be used after @login_required.
    The route must accept a project_id parameter.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        project_id = kwargs.get('project_id')
        if not project_id:
            current_app.logger.error("No project_id provided in route")
            abort(400, "No project_id provided")
        
        # Check if user has access to this project
        if not has_project_access(current_user, project_id):
            current_app.logger.warning(
                f"User {current_user.id} attempted to access project {project_id} without permission"
            )
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def has_project_access(user, project_id):
    """Check if a user has access to a specific project"""
    # Admin users have access to all projects
    if user.is_admin:
        return True
        
    # Check if user is a team member of the project
    from app.models.project import ProjectTeamMember
    member = ProjectTeamMember.query.filter_by(
        project_id=project_id, 
        user_id=user.id
    ).first()
    
    return member is not None