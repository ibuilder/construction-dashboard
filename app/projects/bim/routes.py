from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bim_bp
from app.models.bim import BimModel, CoordinationIssue
from app.models.project import Project
from app.extensions import db
from app.utils.access_control import role_required

@bim_bp.route('/models')
@login_required
def models():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    bim_models = BimModel.query.filter_by(project_id=project_id).all()
    return render_template('projects/bim/models.html', project=project, bim_models=bim_models)

@bim_bp.route('/models/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_model():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        model_name = request.form['model_name']
        new_model = BimModel(name=model_name, project_id=project_id, created_by=current_user.id)
        db.session.add(new_model)
        db.session.commit()
        flash('BIM model created successfully!', 'success')
        return redirect(url_for('projects.bim.models', project_id=project_id))
    return render_template('projects/bim/create_model.html', project=project)

@bim_bp.route('/issues')
@login_required
def issues():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    coordination_issues = CoordinationIssue.query.filter_by(project_id=project_id).all()
    return render_template('projects/bim/issues.html', project=project, coordination_issues=coordination_issues)

@bim_bp.route('/issues/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_issue():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        issue_description = request.form['issue_description']
        new_issue = CoordinationIssue(description=issue_description, project_id=project_id, created_by=current_user.id)
        db.session.add(new_issue)
        db.session.commit()
        flash('Coordination issue created successfully!', 'success')
        return redirect(url_for('projects.bim.issues', project_id=project_id))
    return render_template('projects/bim/create_issue.html', project=project)