from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.bim import BIMModel
from app.projects.bim.forms import BIMUploadForm
import os

bim_bp = Blueprint('bim', __name__, template_folder='templates')

@bim_bp.route('/bim/dashboard')
@login_required
def dashboard():
    """Display the BIM dashboard with available models."""
    models = BIMModel.query.filter_by(user_id=current_user.id).all()
    return render_template('projects/bim/dashboard.html', models=models)

@bim_bp.route('/bim/upload', methods=['GET', 'POST'])
@login_required
def upload_model():
    """Upload a new BIM model."""
    form = BIMUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and file.filename.endswith('.ifc'):
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            new_model = BIMModel(project_id=form.project_id.data, file_path=file_path, user_id=current_user.id)
            new_model.save()
            flash('BIM model uploaded successfully!', 'success')
            return redirect(url_for('bim.dashboard'))
        else:
            flash('Invalid file format. Please upload a .IFC file.', 'danger')
    return render_template('projects/bim/upload.html', form=form)

@bim_bp.route('/bim/model/<int:model_id>')
@login_required
def view_model(model_id):
    """View a specific BIM model."""
    model = BIMModel.query.get_or_404(model_id)
    return render_template('projects/bim/model.html', model=model)