# app/projects/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, send_file, jsonify
from flask_login import login_required, current_user
from app.projects.forms import ProjectForm, ProjectFilterForm, ProjectNoteForm
from app.models.project import Project, ProjectUser, ProjectImage, ProjectNote, ProjectTeamMember
from app.models.user import Role
from app.models.client import Client
from app.extensions import db, cache
from app.utils.access_control import role_required, has_project_access, clear_access_cache
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import shutil
from PIL import Image
from io import BytesIO

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def index():
    """Show list of projects the user has access to"""
    form = ProjectFilterForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query - get projects the user is part of
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        # Admins see all projects
        query = Project.query
    else:
        # Regular users see only projects they're members of
        query = Project.query.join(ProjectTeamMember).filter(ProjectTeamMember.user_id == current_user.id)
    
    # Apply filters if provided
    if form.validate():
        if form.status.data:
            query = query.filter(Project.status == form.status.data)
        if form.client.data:
            query = query.filter(Project.client_id == form.client.data)
        if form.search.data:
            search_term = f"%{form.search.data}%"
            query = query.filter(or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term)
            ))
    permission = {
        'CREATE': Role.PERMISSION['CREATE'],
        'EDIT': Role.PERMISSION['EDIT'],
        'DELETE': Role.PERMISSION['DELETE']
    }
    # Apply sorting
    sort_by = request.args.get('sort_by', 'start_date')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    if hasattr(Project, sort_by) and sort_dir in ['asc', 'desc']:
        column = getattr(Project, sort_by)
        query = query.order_by(column.desc() if sort_dir == 'desc' else column.asc())
    else:
        # Default sorting
        query = query.order_by(Project.start_date.desc())
    
    # Paginate results
    projects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('projects/index.html', 
                          projects=projects, 
                          form=form,
                          sort_by=sort_by,
                          sort_dir=sort_dir, permission = permission)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'project_manager'])
def create():
    """Create a new project"""
    form = ProjectForm()
    
    # Debug form submission
    current_app.logger.info(f"Form submitted: {request.method}")
    
    if form.validate_on_submit():
        current_app.logger.info("Form validated successfully")
        try:
            # Debug form data
            current_app.logger.info(f"Form data - Name: {form.name.data}, Number: {form.number.data}")
            current_app.logger.info(f"Form data - Start date: {form.start_date.data}")
            
            # Create new project
            project = Project()
            form.populate_obj(project)
            
            current_app.logger.info(f"Project object created with name: {project.name}, number: {project.number}")
            
            # Add client mapping if needed
            if form.client_name.data:
                current_app.logger.info(f"Looking up client: {form.client_name.data}")
                client = Client.query.filter_by(name=form.client_name.data).first()
                if client:
                    project.client_id = client.id
                    current_app.logger.info(f"Client found with ID: {client.id}")
                else:
                    current_app.logger.info("Client not found, using client_name directly")
            
            current_app.logger.info("Adding project to database session")
            db.session.add(project)
            db.session.flush()
            current_app.logger.info(f"Project flushed to DB with ID: {project.id}")
            
            # Add current user as project manager
            project_manager = ProjectTeamMember(
                project_id=project.id,
                user_id=current_user.id,
                role='project_manager',
                is_active=True,
                added_by=current_user.id
            )
            current_app.logger.info(f"Creating team member with user ID: {current_user.id}")
            db.session.add(project_manager)
            
            current_app.logger.info("Committing transaction")
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating project: {str(e)}")
            current_app.logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            flash(f'An error occurred while creating the project: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            current_app.logger.warning("Form validation failed")
            for field, errors in form.errors.items():
                current_app.logger.warning(f"Field {field} errors: {errors}")
    
    return render_template('projects/create.html', form=form)

@projects_bp.route('/<int:project_id>')
@login_required
def view(project_id):
    """Project details page that redirects to overview"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    return redirect(url_for('projects_overview.index', project_id=project_id))

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Edit project details"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    # Ensure they have project manager or admin permissions
    team_member = ProjectTeamMember.query.filter_by(
        project_id=project_id, 
        user_id=current_user.id
    ).first()
    
    if not (hasattr(current_user, 'is_admin') and current_user.is_admin) and \
       not (team_member and team_member.role in ['project_manager', 'admin']):
        flash("You don't have permission to edit this project.", "danger")
        return redirect(url_for('projects.view', project_id=project_id))
    
    form = ProjectForm(obj=project)
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    form.client_id.choices.insert(0, (0, 'Select Client'))
    
    if form.validate_on_submit():
        try:
            form.populate_obj(project)
            
            if form.client_id.data == 0:
                project.client_id = None
                
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating project {project_id}: {str(e)}")
            flash('An error occurred while updating the project.', 'danger')
    
    return render_template('projects/edit.html', form=form, project=project)

@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@role_required(['admin'])
def delete(project_id):
    """Delete a project - admin only"""
    project = Project.query.get_or_404(project_id)
    
    try:
        project_name = project.name
        db.session.delete(project)
        db.session.commit()
        
        # Clear access cache for this project
        clear_access_cache(project_id=project_id)
        
        flash(f'Project "{project_name}" has been deleted.', 'success')
        return redirect(url_for('projects.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting project {project_id}: {str(e)}")
        flash('An error occurred while deleting the project.', 'danger')
        return redirect(url_for('projects.view', project_id=project_id))

# API endpoint
@projects_bp.route('/api/projects')
@login_required
def api_projects():
    """API endpoint for getting project data (for select2, etc.)"""
    search = request.args.get('search', '', type=str)
    
    # Base query - get projects the user is part of
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        # Admins see all projects
        query = Project.query
    else:
        # Regular users see only projects they're members of
        query = Project.query.join(ProjectTeamMember).filter(ProjectTeamMember.user_id == current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(Project.name.ilike(f'%{search}%'))
    
    # Get projects
    projects = query.order_by(Project.name).limit(25).all()
    
    # Format for select2
    results = [{'id': p.id, 'text': p.name} for p in projects]
    return jsonify({'results': results})

# Health check endpoints (moved to app-level routes)
# Note: These should be defined at the application level, not the blueprint level
def check_db_connection():
    """Check if database connection is working"""
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception:
        return False

def check_cache_connection():
    """Check if cache connection is working"""
    try:
        cache.set('health_check', 'ok')
        return cache.get('health_check') == 'ok'
    except Exception:
        return False