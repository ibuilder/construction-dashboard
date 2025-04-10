from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import projects_bp
from app.models.project import Project
from app.models.user import User
from app.extensions import db
from app.utils.access_control import role_required
from datetime import datetime

@projects_bp.route('/')
@login_required
def list_projects():
    """Display list of projects the user has access to"""
    # Filter projects based on user role and permissions
    if current_user.role == 'Admin':
        projects = Project.query.order_by(Project.name).all()
    else:
        projects = Project.query.join(Project.users).filter(User.id == current_user.id).order_by(Project.name).all()
    
    return render_template('projects/list.html', projects=projects)

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative'])
def create_project():
    """Create a new project"""
    from .forms import ProjectForm
    
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            number=form.number.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            owner_id=form.owner_id.data,
            created_by=current_user.id
        )
        # Add current user to project
        project.users.append(current_user)
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.view_project', id=project.id))
    
    return render_template('projects/create.html', form=form)

@projects_bp.route('/<int:id>')
@login_required
def view_project(id):
    """Display project dashboard with summary of all modules"""
    project = Project.query.get_or_404(id)
    
    # Check if user has access to this project
    if not current_user.role == 'Admin' and current_user not in project.users:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    # Get summary data for dashboard
    summary = {
        'rfis': {
            'total': project.rfis.count(),
            'open': project.rfis.filter_by(status='open').count(),
        },
        'submittals': {
            'total': project.submittals.count(),
            'pending': project.submittals.filter_by(status='pending').count(),
        },
        'changes': {
            'total': project.change_orders.count(),
            'pending': project.change_orders.filter_by(status='pending').count(),
            'value': sum(co.amount for co in project.change_orders if co.status == 'approved')
        },
        'daily_reports': {
            'total': project.daily_reports.count(),
            'last': project.daily_reports.order_by(db.desc('report_date')).first()
        },
    }
    
    return render_template('projects/view.html', project=project, summary=summary)

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def edit_project(id):
    """Edit project details"""
    from .forms import ProjectForm
    
    project = Project.query.get_or_404(id)
    
    # Check if user has access to edit this project
    if not current_user.role == 'Admin' and current_user not in project.users:
        flash('You do not have permission to edit this project', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.updated_by = current_user.id
        project.updated_at = datetime.now()
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view_project', id=project.id))
    
    return render_template('projects/edit.html', form=form, project=project)

@projects_bp.route('/<int:id>/users')
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def project_users(id):
    """Manage users associated with a project"""
    project = Project.query.get_or_404(id)
    
    # Check if user has access to manage project users
    if not current_user.role == 'Admin' and current_user not in project.users:
        flash('You do not have permission to manage project users', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/users.html', project=project)

@projects_bp.route('/<int:id>/users/add', methods=['POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def add_project_user(id):
    """Add user to project"""
    project = Project.query.get_or_404(id)
    
    # Check if user has access to manage project users
    if not current_user.role == 'Admin' and current_user not in project.users:
        return jsonify({'success': False, 'message': 'You do not have permission to manage project users'})
    
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    if user in project.users:
        return jsonify({'success': False, 'message': 'User is already assigned to this project'})
    
    project.users.append(user)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'User added successfully',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    })

@projects_bp.route('/<int:id>/users/remove', methods=['POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def remove_project_user(id):
    """Remove user from project"""
    project = Project.query.get_or_404(id)
    
    # Check if user has access to manage project users
    if not current_user.role == 'Admin' and current_user not in project.users:
        return jsonify({'success': False, 'message': 'You do not have permission to manage project users'})
    
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    if user == current_user and current_user.role != 'Admin':
        return jsonify({'success': False, 'message': 'You cannot remove yourself from the project'})
    
    if user not in project.users:
        return jsonify({'success': False, 'message': 'User is not assigned to this project'})
    
    project.users.remove(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User removed successfully'})