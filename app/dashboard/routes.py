from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.user import User
from app.models.engineering import RFI, Submittal
from app.models.field import DailyReport, Punchlist
from app.models.safety import SafetyObservation, IncidentReport
from app.models.cost import Invoice, PotentialChangeOrder, ChangeOrder
from app.extensions import db, cache
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    # Get user's projects
    user_projects = [pu.project for pu in current_user.projects.all()]
    
    # Get recent activity (implementation needed)
    recent_activity = []
    
    # Get important notifications (implementation needed)
    notifications = []
    
    # Get upcoming deadlines (implementation needed)
    upcoming_deadlines = []
    
    return render_template('dashboard/index.html',
                          projects=user_projects,
                          activity=recent_activity,
                          notifications=notifications,
                          deadlines=upcoming_deadlines)

@dashboard_bp.route('/my-tasks')
@login_required
def my_tasks():
    """Dashboard showing tasks assigned to the current user"""
    # Get RFIs assigned to current user
    assigned_rfis = RFI.query.filter_by(assigned_to=current_user.id, status='open').all()
    
    # Get submittals assigned to current user
    assigned_submittals = Submittal.query.filter_by(assigned_to=current_user.id, status='pending').all()
    
    # Get punchlist items assigned to current user
    assigned_punchlists = Punchlist.query.join(Punchlist.items).filter(
        Punchlist.items.assigned_to == current_user.id,
        Punchlist.items.status == 'open'
    ).all()
    
    return render_template('dashboard/my_tasks.html',
                          assigned_rfis=assigned_rfis,
                          assigned_submittals=assigned_submittals,
                          assigned_punchlists=assigned_punchlists)

@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('dashboard/profile.html')