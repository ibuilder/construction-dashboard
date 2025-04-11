from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, send_file
from flask_login import login_required, current_user
from app.projects.forms import ProjectForm, ProjectFilterForm, ProjectNoteForm
from app.models.project import Project, ProjectUser, ProjectImage, ProjectNote
from app.models.user import Role
from app.extensions import db, cache
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
    """Show list of projects"""
    form = ProjectFilterForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Get base query - filter by user access unless admin
    if current_user.is_admin():
        query = Project.query
    else:
        project_ids = [pu.project_id for pu in current_user.projects]
        query = Project.query.filter(Project.id.in_(project_ids))
    
    # Apply filters if provided
    if form.status.data:
        query = query.filter(Project.status == form.status.data)
    
    if form.project_type.data:
        query = query.filter(Project.project_type == form.project_type.data)
    
    if form.search.data:
        search_term = f"%{form.search.data}%"
        query = query.filter(
            (Project.name.ilike(search_term)) |
            (Project.number.ilike(search_term)) |
            (Project.client_name.ilike(search_term))
        )
    
    # Order by status (active first), then by updated date
    query = query.order_by(
        # Active projects first, then planning, on hold, completed, cancelled
        db.case(
            (Project.status == 'active', 1),
            (Project.status == 'planning', 2),
            (Project.status == 'on_hold', 3),
            (Project.status == 'completed', 4),
            (Project.status == 'cancelled', 5),
            else_=6
        ),
        Project.updated_at.desc()
    )
    
    # Pagination
    projects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('projects/index.html', 
                          projects=projects,
                          form=form)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new project"""
    # Check if user has permission to create projects
    if not current_user.can(Role.PERMISSION['CREATE']):
        flash('You do not have permission to create projects.', 'danger')
        return redirect(url_for('projects.index'))
    
    form = ProjectForm()
    
    if form.validate_on_submit():
        # Create a new project
        project = Project(
            name=form.name.data,
            number=form.number.data,
            description=form.description.data,
            status=form.status.data,
            client_name=form.client_name.data,
            client_contact_info=form.client_contact_info.data,
            start_date=form.start_date.data,
            target_completion_date=form.target_completion_date.data,
            actual_completion_date=form.actual_completion_date.data,
            contract_amount=form.contract_amount.data,
            project_type=form.project_type.data,
            category=form.category.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            country=form.country.data,
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID without committing
        
        # Add creator as project manager
        project_user = ProjectUser(
            user_id=current_user.id,
            project_id=project.id,
            role='manager'
        )
        db.session.add(project_user)
        
        # Add team members
        if form.team_members.data:
            for user_id in form.team_members.data:
                if user_id != current_user.id:  # Skip if user is already added as manager
                    team_member = ProjectUser(
                        user_id=user_id,
                        project_id=project.id,
                        role='member'
                    )
                    db.session.add(team_member)
        
        # Process contract document
        if form.contract_document.data:
            contract_document = form.contract_document.data
            filename = secure_filename(contract_document.filename)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create directory if it doesn't exist
            document_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', str(project.id))
            os.makedirs(document_dir, exist_ok=True)
            
            # Save the file
            contract_document.save(os.path.join(document_dir, unique_filename))
            
            # Update project with document info
            project.contract_document_filename = filename
            project.contract_document_path = os.path.join('documents', str(project.id), unique_filename)
        
        # Process project images
        if form.project_images.data and form.project_images.data[0]:
            for image_file in form.project_images.data:
                if image_file.filename:
                    # Process and save image
                    image_filename = save_project_image(image_file, project.id)
                    
                    # Create image record
                    image = ProjectImage(
                        project_id=project.id,
                        filename=os.path.basename(image_filename),
                        path=image_filename
                    )
                    db.session.add(image)
        
        db.session.commit()
        flash(f"Project '{project.name}' has been created successfully.", 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    return render_template('projects/create.html', form=form)

@projects_bp.route('/<int:id>')
@login_required
def view(id):
    """View a project"""
    project = get_project_or_404(id)
    
    # Get team members
    team = ProjectUser.query.filter_by(project_id=id).all()
    
    # Get project notes, ordered by newest first
    notes = ProjectNote.query.filter_by(project_id=id).order_by(ProjectNote.created_at.desc()).all()
    
    # Get images
    images = ProjectImage.query.filter_by(project_id=id).all()
    
    # Note form
    note_form = ProjectNoteForm()
    
    return render_template('projects/view.html', 
                          project=project,
                          team=team,
                          notes=notes,
                          images=images,
                          note_form=note_form)

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a project"""
    project = get_project_or_404(id)
    
    # Check if user has permission to edit this project
    if not (current_user.is_admin() or is_project_manager(project.id, current_user.id)):
        flash('You do not have permission to edit this project.', 'danger')
        return redirect(url_for('projects.view', id=id))
    
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        # Update basic information
        project.name = form.name.data
        project.number = form.number.data
        project.description = form.description.data
        project.status = form.status.data
        project.client_name = form.client_name.data
        project.client_contact_info = form.client_contact_info.data
        
        # Update dates
        project.start_date = form.start_date.data
        project.target_completion_date = form.target_completion_date.data
        project.actual_completion_date = form.actual_completion_date.data
        
        # Update financial information
        project.contract_amount = form.contract_amount.data
        
        # Update classification
        project.project_type = form.project_type.data
        project.category = form.category.data
        
        # Update location
        project.address = form.address.data
        project.city = form.city.data
        project.state = form.state.data
        project.zip_code = form.zip_code.data
        project.country = form.country.data
        
        # Update timestamp
        project.updated_at = datetime.utcnow()
        
        # Process contract document
        if form.contract_document.data:
            contract_document = form.contract_document.data
            filename = secure_filename(contract_document.filename)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create directory if it doesn't exist
            document_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', str(project.id))
            os.makedirs(document_dir, exist_ok=True)
            
            # Delete old file if exists
            if project.contract_document_path:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], project.contract_document_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Save the file
            contract_document.save(os.path.join(document_dir, unique_filename))
            
            # Update project with document info
            project.contract_document_filename = filename
            project.contract_document_path = os.path.join('documents', str(project.id), unique_filename)
        
        # Process project images
        if form.project_images.data and form.project_images.data[0]:
            for image_file in form.project_images.data:
                if image_file.filename:
                    # Process and save image
                    image_filename = save_project_image(image_file, project.id)
                    
                    # Create image record
                    image = ProjectImage(
                        project_id=project.id,
                        filename=os.path.basename(image_filename),
                        path=image_filename
                    )
                    db.session.add(image)
        
        # Update team members
        # First, get existing team members excluding the manager
        existing_team = [pu.user_id for pu in ProjectUser.query.filter(
            ProjectUser.project_id == project.id,
            ProjectUser.role != 'manager'
        ).all()]
        
        # Remove team members not in the form data
        for user_id in existing_team:
            if user_id not in form.team_members.data:
                ProjectUser.query.filter_by(
                    project_id=project.id, 
                    user_id=user_id
                ).delete()
        
        # Add new team members
        for user_id in form.team_members.data:
            # Skip if already a team member
            if user_id in existing_team:
                continue
                
            # Skip if user is the project manager
            if is_project_manager(project.id, user_id):
                continue
                
            team_member = ProjectUser(
                user_id=user_id,
                project_id=project.id,
                role='member'
            )
            db.session.add(team_member)
        
        db.session.commit()
        flash(f"Project '{project.name}' has been updated successfully.", 'success')
        return redirect(url_for('projects.view', id=id))
    
    # Pre-select currently assigned team members
    team_member_ids = [pu.user_id for pu in ProjectUser.query.filter(
        ProjectUser.project_id == project.id,
        ProjectUser.role != 'manager'  # Exclude the manager
    ).all()]
    form.team_members.data = team_member_ids
    
    return render_template('projects/edit.html', form=form, project=project)

@projects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a project"""
    project = get_project_or_404(id)
    
    # Check if user has permission to delete
    if not current_user.can(Role.PERMISSION['DELETE']):
        flash('You do not have permission to delete projects.', 'danger')
        return redirect(url_for('projects.view', id=id))
    
    # Get project name before deletion for the flash message
    project_name = project.name
    
    # Delete project directory with all files
    project_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', str(id))
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    
    # Delete project images directory
    images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', str(id))
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    
    # Delete project from database
    db.session.delete(project)
    db.session.commit()
    
    flash(f"Project '{project_name}' has been deleted.", 'success')
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:id>/add-note', methods=['POST'])
@login_required
def add_note(id):
    """Add a note to a project"""
    project = get_project_or_404(id)
    form = ProjectNoteForm()
    
    if form.validate_on_submit():
        note = ProjectNote(
            project_id=id,
            user_id=current_user.id,
            content=form.content.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully.', 'success')
    
    return redirect(url_for('projects.view', id=id))

@projects_bp.route('/<int:id>/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(id, note_id):
    """Delete a project note"""
    project = get_project_or_404(id)
    note = ProjectNote.query.get_or_404(note_id)
    
    # Check if user has permission to delete the note
    if note.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this note.', 'danger')
        return redirect(url_for('projects.view', id=id))
    
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'success')
    return redirect(url_for('projects.view', id=id))

@projects_bp.route('/<int:id>/download/<document_type>')
@login_required
def download_document(id, document_type):
    """Download a project document"""
    project = get_project_or_404(id)
    
    if document_type == 'contract':
        if not project.contract_document_path:
            flash('No contract document available.', 'warning')
            return redirect(url_for('projects.view', id=id))
        
        document_path = os.path.join(current_app.config['UPLOAD_FOLDER'], project.contract_document_path)
        if not os.path.exists(document_path):
            flash('Document file not found.', 'warning')
            return redirect(url_for('projects.view', id=id))
        
        return send_file(document_path, download_name=project.contract_document_filename)
    
    # Add other document types here
    
    abort(404)

@projects_bp.route('/<int:id>/image/<path:filename>')
@login_required
def get_image(id, filename):
    """Get a project image"""
    project = get_project_or_404(id)
    
    # Check if image belongs to this project
    image = ProjectImage.query.filter_by(project_id=id, filename=filename).first_or_404()
    
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', str(id), filename)
    if not os.path.exists(image_path):
        abort(404)
    
    return send_file(image_path)

@projects_bp.route('/<int:id>/delete-image', methods=['POST'])
@login_required
def delete_image(id):
    """Delete a project image"""
    project = get_project_or_404(id)
    
    # Check if user has permission to edit this project
    if not (current_user.is_admin() or is_project_manager(project.id, current_user.id)):
        flash('You do not have permission to modify this project.', 'danger')
        return redirect(url_for('projects.view', id=id))
    
    image_id = request.form.get('image_id')
    image = ProjectImage.query.get_or_404(image_id)
    
    # Check if image belongs to this project
    if image.project_id != id:
        abort(404)
    
    # Delete image file
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', str(id), image.filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Delete image from database
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('projects.edit', id=id))

# Helper functions
def get_project_or_404(project_id):
    """Get a project by ID and check user access"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if not current_user.is_admin():
        project_user = ProjectUser.query.filter_by(
            project_id=project_id, 
            user_id=current_user.id
        ).first()
        
        if not project_user:
            abort(403)
    
    return project

def is_project_manager(project_id, user_id):
    """Check if a user is a manager for a project"""
    project_user = ProjectUser.query.filter_by(
        project_id=project_id,
        user_id=user_id,
        role='manager'
    ).first()
    
    return project_user is not None

def save_project_image(image_file, project_id):
    """Process and save a project image
    
    Returns the relative path to the saved image
    """
    filename = secure_filename(image_file.filename)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Create directory if it doesn't exist
    image_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', str(project_id))
    os.makedirs(image_dir, exist_ok=True)
    
    # Path to save the image
    image_path = os.path.join(image_dir, unique_filename)
    
    # Process image to standardize and optimize
    img = Image.open(image_file)
    
    # Resize large images to a maximum dimension
    max_dimension = 1920  # Full HD width
    if img.width > max_dimension or img.height > max_dimension:
        ratio = min(max_dimension / img.width, max_dimension / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Save the processed image
    img.save(image_path, optimize=True, quality=85)
    
    # Return the relative path
    return os.path.join('photos', str(project_id), unique_filename)