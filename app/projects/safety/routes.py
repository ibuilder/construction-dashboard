from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from . import safety_bp
from .forms import SafetyObservationForm, IncidentReportForm, JobHazardAnalysisForm, PreTaskPlanForm
from app.models.safety import (
    SafetyObservation, IncidentReport, JobHazardAnalysis, PreTaskPlan,
    EmployeeOrientation, SafetyMetric
)
from app.models.base import Comment, Attachment
from app.models.project import Project
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from app.utils.email_notifications import send_safety_alert
from datetime import datetime, timedelta
import os
import uuid

# Safety Dashboard
@safety_bp.route('/dashboard')
@login_required
def dashboard():
    """Safety dashboard with summary of all modules"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get counts for all safety modules
    observations_count = SafetyObservation.query.filter_by(project_id=project_id).count()
    incidents_count = IncidentReport.query.filter_by(project_id=project_id).count()
    jha_count = JobHazardAnalysis.query.filter_by(project_id=project_id).count()
    pretask_count = PreTaskPlan.query.filter_by(project_id=project_id).count()
    orientation_count = EmployeeOrientation.query.filter_by(project_id=project_id).count()
    
    # Get safety metrics
    metrics = SafetyMetric.query.filter_by(project_id=project_id).order_by(
        SafetyMetric.date.desc()).limit(12).all()
    
    # Calculate incident rates
    total_hours = sum(metric.man_hours for metric in metrics)
    recordable_incidents = sum(metric.recordable_incidents for metric in metrics)
    lost_time_incidents = sum(metric.lost_time_incidents for metric in metrics)
    
    trir = (recordable_incidents * 200000 / total_hours) if total_hours > 0 else 0
    ltir = (lost_time_incidents * 200000 / total_hours) if total_hours > 0 else 0
    
    # Get safety observation types for chart
    observation_types = db.session.query(
        SafetyObservation.category, db.func.count(SafetyObservation.id)
    ).filter_by(project_id=project_id).group_by(SafetyObservation.category).all()
    
    # Format for chart
    type_labels = [category for category, _ in observation_types]
    type_data = [count for _, count in observation_types]
    
    # Get recent incidents
    recent_incidents = IncidentReport.query.filter_by(
        project_id=project_id
    ).order_by(IncidentReport.incident_date.desc()).limit(5).all()
    
    # Get monthly metrics for trend chart
    months = []
    recordables_data = []
    manhours_data = []
    
    for metric in reversed(metrics):
        months.append(metric.date.strftime('%b %Y'))
        recordables_data.append(metric.recordable_incidents)
        manhours_data.append(metric.man_hours / 1000)  # Convert to thousands for readability
    
    return render_template('projects/safety/dashboard.html',
                          project=project,
                          observations_count=observations_count,
                          incidents_count=incidents_count,
                          jha_count=jha_count,
                          pretask_count=pretask_count,
                          orientation_count=orientation_count,
                          trir=trir,
                          ltir=ltir,
                          type_labels=type_labels,
                          type_data=type_data,
                          recent_incidents=recent_incidents,
                          months=months,
                          recordables_data=recordables_data,
                          manhours_data=manhours_data)

# Safety Observations
@safety_bp.route('/observations')
@login_required
def observations():
    """List all safety observations"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    observations = SafetyObservation.query.filter_by(project_id=project_id).order_by(
        SafetyObservation.observation_date.desc()).all()
    
    return render_template('projects/safety/observations/list.html',
                          project=project, observations=observations)

@safety_bp.route('/observations/create', methods=['GET', 'POST'])
@login_required
def create_observation():
    """Create a new safety observation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = SafetyObservationForm()
    
    if form.validate_on_submit():
        observation = SafetyObservation(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            observation_date=form.observation_date.data or datetime.now().date(),
            location=form.location.data,
            category=form.category.data,
            severity=form.severity.data,
            status='open',
            observed_by=current_user.id,
            created_by=current_user.id
        )
        db.session.add(observation)
        db.session.commit()
        
        # If severe, send notification
        if form.severity.data in ['critical', 'high']:
            send_safety_alert(observation)
        
        flash('Safety observation recorded successfully!', 'success')
        return redirect(url_for('projects.safety.observations', project_id=project_id))
    
    return render_template('projects/safety/observations/create.html',
                          project=project, form=form)

@safety_bp.route('/observations/<int:id>')
@login_required
def view_observation(id):
    """View a safety observation"""
    observation = SafetyObservation.query.get_or_404(id)
    project = Project.query.get_or_404(observation.project_id)
    
    comments = Comment.query.filter_by(record_type='safety_observation', record_id=id).order_by(
        Comment.created_at).all()
    attachments = Attachment.query.filter_by(record_type='safety_observation', record_id=id).all()
    
    return render_template('projects/safety/observations/view.html',
                          project=project, observation=observation,
                          comments=comments, attachments=attachments)

# Incident Reports
@safety_bp.route('/incidents')
@login_required
def incidents():
    """List all incident reports"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    incidents = IncidentReport.query.filter_by(project_id=project_id).order_by(
        IncidentReport.incident_date.desc()).all()
    
    return render_template('projects/safety/incidents/list.html',
                          project=project, incidents=incidents)

@safety_bp.route('/incidents/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_incident():
    """Create a new incident report"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = IncidentReportForm()
    
    if form.validate_on_submit():
        incident = IncidentReport(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            incident_date=form.incident_date.data,
            incident_time=form.incident_time.data,
            location=form.location.data,
            type=form.type.data,
            severity=form.severity.data,
            reported_by_name=form.reported_by_name.data,
            reported_by_title=form.reported_by_title.data,
            witness_names=form.witness_names.data,
            root_cause=form.root_cause.data,
            corrective_actions=form.corrective_actions.data,
            is_osha_recordable=form.is_osha_recordable.data,
            is_lost_time=form.is_lost_time.data,
            reported_to_authorities=form.reported_to_authorities.data,
            created_by=current_user.id
        )
        db.session.add(incident)
        db.session.commit()
        
        # If OSHA recordable or lost time, update safety metrics
        if form.is_osha_recordable.data or form.is_lost_time.data:
            # Find or create a safety metric for the month of the incident
            month_start = incident.incident_date.replace(day=1)
            metric = SafetyMetric.query.filter_by(
                project_id=project_id, 
                date=month_start
            ).first()
            
            if not metric:
                metric = SafetyMetric(
                    project_id=project_id,
                    date=month_start,
                    man_hours=0,
                    recordable_incidents=0,
                    lost_time_incidents=0,
                    created_by=current_user.id
                )
                db.session.add(metric)
            
            if form.is_osha_recordable.data:
                metric.recordable_incidents += 1
            if form.is_lost_time.data:
                metric.lost_time_incidents += 1
                
            db.session.commit()
        
        flash('Incident report created successfully!', 'success')
        return redirect(url_for('projects.safety.incidents', project_id=project_id))
    
    return render_template('projects/safety/incidents/create.html',
                          project=project, form=form)