from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app.models.bim import BIMModel, BIMModelVersion, BIMIssue
from app.models.project import Project
from app.projects.bim.forms import BIMUploadForm
from app.extensions import db
from app.utils.access_control import project_access_required
from app.utils.file_upload import save_file, ensure_directory_exists
import os
import datetime

bim_bp = Blueprint('bim', __name__)

@bim_bp.route('/bim')
@login_required
@project_access_required
def index(project_id):
    """Display the BIM dashboard with available models."""
    project = Project.query.get_or_404(project_id)
    
    try:
        bim_models = BIMModel.query.filter_by(project_id=project_id).all()
        
        # Calculate storage statistics
        storage_used = sum(model.calculate_storage_size() for model in bim_models)
        storage_used_formatted = f"{storage_used / (1024*1024):.2f} MB" if storage_used > 0 else "0 MB"
        
        return render_template('projects/bim/dashboard.html', 
                               project=project, 
                               bim_models=bim_models,
                               storage_used=storage_used_formatted)
    except Exception as e:
        current_app.logger.error(f"Error in BIM index: {str(e)}")
        flash('An error occurred while loading BIM models.', 'danger')
        return render_template('projects/bim/dashboard.html', 
                               project=project, 
                               bim_models=[],
                               storage_used="0 MB",
                               error=True)

@bim_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@project_access_required
def upload_model(project_id):
    """Upload a new BIM model."""
    project = Project.query.get_or_404(project_id)
    form = BIMUploadForm()
    
    if form.validate_on_submit():
        try:
            file = form.file.data
            if file and file.filename.endswith('.ifc'):
                # Use proper file path management and ensure directory exists
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bim', str(project_id))
                ensure_directory_exists(upload_dir)
                
                # Generate a unique filename to avoid collisions
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(upload_dir, filename)
                
                # Save the file
                file.save(file_path)
                
                # Create new BIM model with DB transaction
                new_model = BIMModel(
                    name=form.name.data,
                    model_type=form.model_type.data,
                    project_id=project_id,
                    user_id=current_user.id
                )
                db.session.add(new_model)
                db.session.flush()  # Get the model ID
                
                # Create initial version
                initial_version = BIMModelVersion(
                    model_id=new_model.id,
                    version_number=1,
                    file_path=file_path,
                    notes="Initial version",
                    user_id=current_user.id
                )
                db.session.add(initial_version)
                db.session.flush()
                
                # Set the current version
                new_model.current_version_id = initial_version.id
                
                db.session.commit()
                
                flash('BIM model uploaded successfully!', 'success')
                return redirect(url_for('projects.bim.index', project_id=project_id))
            else:
                flash('Invalid file format. Please upload a .IFC file.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading BIM model: {str(e)}")
            flash('An error occurred while uploading the model.', 'danger')
    
    return render_template('projects/bim/upload.html', form=form, project=project)

@bim_bp.route('/model/<int:model_id>')
@login_required
@project_access_required
def view_model(project_id, model_id):
    """View a specific BIM model."""
    project = Project.query.get_or_404(project_id)
    model = BIMModel.query.get_or_404(model_id)
    
    # Verify the model belongs to the project
    if model.project_id != int(project_id):
        flash('Model does not belong to this project', 'danger')
        return redirect(url_for('projects.bim.index', project_id=project_id))
    
    # Get the current version or the latest
    version = model.get_current_version()
    if not version:
        flash('No versions available for this model', 'warning')
        return redirect(url_for('projects.bim.index', project_id=project_id))
    
    return render_template('projects/bim/viewer.html', 
                           project=project, 
                           model=model,
                           version=version)

@bim_bp.route('/model/<int:model_id>/file/<int:version_id>')
@login_required
@project_access_required
def get_model_file(project_id, model_id, version_id):
    """Return the actual model file for the viewer."""
    model = BIMModel.query.get_or_404(model_id)
    version = BIMModelVersion.query.get_or_404(version_id)
    
    if model.project_id != int(project_id) or version.model_id != model.id:
        return "Unauthorized", 403
    
    # Check if file exists
    if not os.path.exists(version.file_path):
        return "File not found", 404
    
    return send_file(version.file_path, as_attachment=False)