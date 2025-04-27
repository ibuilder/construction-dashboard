from functools import wraps
from flask import current_app, flash, redirect, url_for, request, abort
from flask_login import current_user

def project_access_required(view_function):
    """
    Decorator to check if user has access to a project
    Expects 'project_id' in the route parameters
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        project_id = kwargs.get('project_id')
        
        if not project_id:
            abort(400, "Project ID is required")
        
        # Import here to avoid circular imports
        from app.models.projects import Project
        
        # Check if project exists
        project = Project.query.get_or_404(project_id)
        
        # Check if user has access to this project
        if not current_user.has_project_access(project):
            flash('You do not have access to this project.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Add project to kwargs for convenience
        kwargs['project'] = project
        
        return view_function(*args, **kwargs)
    
    return decorated_function

def role_required(*roles):
    """
    Decorator to check if user has any of the required roles
    Usage: @role_required('admin', 'manager')
    """
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not any(current_user.has_role(role) for role in roles):
                flash('You do not have permission to access this resource.', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return view_function(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def admin_required(view_function):
    """
    Decorator to check if user has admin role
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.has_role('admin'):
            flash('Administrator access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return view_function(*args, **kwargs)
    
    return decorated_function

def owner_or_admin_required(model_class):
    """
    Decorator to check if user is the owner of a resource or has admin role
    Usage: @owner_or_admin_required(SomeModel)
    Expects 'id' in the route parameters
    """
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            resource_id = kwargs.get('id')
            if not resource_id:
                abort(400, "Resource ID is required")
            
            resource = model_class.query.get_or_404(resource_id)
            
            # Check if user is the creator/owner of the resource or has admin role
            is_owner = hasattr(resource, 'created_by') and resource.created_by == current_user.id
            
            if not (is_owner or current_user.has_role('admin')):
                flash('You do not have permission to modify this resource.', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return view_function(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def has_project_permission(permission):
    """
    Decorator to check if user has specific permission for a project
    Usage: @has_project_permission('edit_project')
    Expects 'project_id' in the route parameters
    """
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            project_id = kwargs.get('project_id')
            
            if not project_id:
                abort(400, "Project ID is required")
            
            # Import here to avoid circular imports
            from app.models.projects import Project
            
            # Check if project exists
            project = Project.query.get_or_404(project_id)
            
            # Check if user has the specific permission for this project
            if not current_user.has_project_permission(project, permission):
                flash(f'You do not have {permission} permission for this project.', 'danger')
                return redirect(url_for('projects.view', project_id=project_id))
            
            # Add project to kwargs for convenience
            kwargs['project'] = project
            
            return view_function(*args, **kwargs)
        
        return decorated_function
    
    return decorator