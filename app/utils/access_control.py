## Utility Files

### Access Control
from functools import wraps
from flask import flash, redirect, url_for, abort, request, current_app
from flask_login import current_user
import functools

# Cache for project access to reduce database queries
_project_access_cache = {}

def role_required(roles):
    """
    Decorator for views that checks if the logged in user has the required role
    
    Args:
        roles: List or string of role(s) that can access the route
    """
    if isinstance(roles, str):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('auth.login', next=request.url))
            
            # Check if user has any of the required roles
            if not (hasattr(current_user, 'role') and 
                   (current_user.role in roles or 
                    (hasattr(current_user, 'is_admin') and current_user.is_admin))):
                current_app.logger.warning(
                    f"User {current_user.id} attempted to access a restricted page requiring roles: {roles}"
                )
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
            abort(400, description="No project_id provided")
        
        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            current_app.logger.error(f"Invalid project_id format: {project_id}")
            abort(400, description="Invalid project ID format")
            
        # Check if user has access to this project
        if not has_project_access(current_user, project_id):
            current_app.logger.warning(
                f"User {current_user.id} attempted to access project {project_id} without permission"
            )
            abort(403, description="You don't have access to this project")
            
        return f(*args, **kwargs)
    return decorated_function

def clear_access_cache(user_id=None, project_id=None):
    """
    Clear the project access cache, either completely or for a specific user/project
    
    Args:
        user_id: Optional user ID to clear cache for specific user
        project_id: Optional project ID to clear cache for specific project
    """
    global _project_access_cache
    
    if user_id is None and project_id is None:
        # Clear entire cache
        _project_access_cache = {}
    elif user_id is not None and project_id is not None:
        # Clear specific user-project combination
        _project_access_cache.pop(f"{user_id}:{project_id}", None)
    elif user_id is not None:
        # Clear all entries for this user
        keys_to_remove = [k for k in _project_access_cache if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            _project_access_cache.pop(key, None)
    elif project_id is not None:
        # Clear all entries for this project
        keys_to_remove = [k for k in _project_access_cache if k.endswith(f":{project_id}")]
        for key in keys_to_remove:
            _project_access_cache.pop(key, None)

def has_project_access(user, project_id):
    """
    Check if a user has access to a specific project
    
    Args:
        user: User object to check permissions for
        project_id: ID of the project to check access for
        
    Returns:
        bool: True if the user has access, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
        
    # Check cache first
    cache_key = f"{user.id}:{project_id}"
    if cache_key in _project_access_cache:
        return _project_access_cache[cache_key]
    
    # Admin users have access to all projects
    if hasattr(user, 'is_admin') and user.is_admin:
        _project_access_cache[cache_key] = True
        return True
    
    try:
        # Check if user is a team member of the project
        from app.models.project import ProjectTeamMember
        member = ProjectTeamMember.query.filter_by(
            project_id=project_id, 
            user_id=user.id
        ).first()
        
        result = member is not None
        
        # Cache the result to avoid repeated database queries
        _project_access_cache[cache_key] = result
        return result
        
    except Exception as e:
        current_app.logger.error(f"Error checking project access: {str(e)}")
        # Don't cache errors
        return False