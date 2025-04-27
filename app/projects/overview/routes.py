# app/projects/overview/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from app.models.project import Project, ProjectTeamMember
from app.extensions import db
from app.utils.access_control import has_project_access
from datetime import datetime

overview_bp = Blueprint('projects_overview', __name__)

@overview_bp.route('/<int:project_id>/overview')
@login_required
def index(project_id):
    """Project overview page"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
    
    # Check if user is project manager
    is_project_manager = False
    project_user = ProjectTeamMember.query.filter_by(
        project_id=project_id,
        user_id=current_user.id,
        role='project_manager'
    ).first()
    
    if project_user or (hasattr(current_user, 'is_admin') and current_user.is_admin):
        is_project_manager = True
    
    # Get project team members
    project_users = ProjectTeamMember.query.filter_by(project_id=project_id).all()
    
    # Get counts for badges
    # These would typically come from your models
    try:
        from app.models.engineering import RFI
        rfi_count = RFI.query.filter_by(project_id=project_id, status='open').count()
    except:
        rfi_count = None
        
    try:
        from app.models.field import DailyReport
        daily_report_count = DailyReport.query.filter_by(project_id=project_id).count()
    except:
        daily_report_count = None
        
    try:
        from app.models.safety import SafetyObservation
        safety_observation_count = SafetyObservation.query.filter_by(
            project_id=project_id, 
            status='open'
        ).count()
    except:
        safety_observation_count = None
        
    try:
        from app.models.cost import ChangeOrder
        change_order_count = ChangeOrder.query.filter_by(project_id=project_id).count()
    except:
        change_order_count = None
    
    # Get today for timeline comparisons
    today = datetime.now().date()
    
    return render_template('projects/overview/index.html',
                          project=project,
                          is_project_manager=is_project_manager,
                          project_users=project_users,
                          today=today,
                          rfi_count=rfi_count,
                          daily_report_count=daily_report_count,
                          safety_observation_count=safety_observation_count,
                          change_order_count=change_order_count)
