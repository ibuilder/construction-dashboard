from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.user import User
from app.models.safety import (
    SafetyObservation, IncidentReport, JobHazardAnalysis, JHAStep,
    PreTaskPlan, PreTaskAttendee, SafetyOrientation, OrientationAttendee,
    SafetyMetrics, IncidentPhoto, SafetyPhoto, ObservationType, IncidentType, SafetySeverity, SafetyStatus
)
from app.projects.safety.forms import (
    SafetyObservationForm, IncidentReportForm, JobHazardAnalysisForm, JHAStepForm,
    PreTaskPlanForm, AttendeeForm, SafetyOrientationForm, SafetyMetricsForm,
    ObservationStatusForm
)
from app.extensions import db
from app.utils.access_control import project_access_required
from app.utils.file_upload import save_file, get_file_url, delete_file
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
import calendar
import os
import uuid

safety_bp = Blueprint('projects.safety', __name__)

@safety_bp.route('/dashboard')
@login_required
@project_access_required
def dashboard():
    """Safety dashboard view"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get counts for widgets
    observations_count = SafetyObservation.query.filter_by(project_id=project_id).count()
    incidents_count = IncidentReport.query.filter_by(project_id=project_id).count()
    jha_count = JobHazardAnalysis.query.filter_by(project_id=project_id).count()
    pretask_count = PreTaskPlan.query.filter_by(project_id=project_id).count()
    orientation_count = SafetyOrientation.query.filter_by(project_id=project_id).count()
    
    # Get latest metrics for TRIR and LTIR calculation
    latest_metrics = SafetyMetrics.query.filter_by(project_id=project_id).order_by(
        SafetyMetrics.date.desc()).first()
    
    # Calculate project-to-date metrics if any metrics exist
    trir = 0
    ltir = 0
    
    metrics = SafetyMetrics.query.filter_by(project_id=project_id).order_by(
        SafetyMetrics.date.desc()).limit(12).all()
    
    if metrics:
        total_hours = sum(metric.man_hours for metric in metrics)
        total_recordables = sum(metric.recordable_incidents for metric in metrics)
        total_lost_time = sum(metric.lost_time_incidents for metric in metrics)
        
        if total_hours > 0:
            trir = (total_recordables * 200000) / total_hours
            ltir = (total_lost_time * 200000) / total_hours
    
    # Get observation types for chart
    observation_types = db.session.query(
        SafetyObservation.category, 
        func.count(SafetyObservation.id)
    ).filter_by(
        project_id=project_id
    ).group_by(SafetyObservation.category).all()
    
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

# Safety Observations routes
@safety_bp.route('/observations')
@login_required
@project_access_required
def observations():
    """List all safety observations"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Apply filters if provided
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    severity_filter = request.args.get('severity', 'all')
    
    query = SafetyObservation.query.filter_by(project_id=project_id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    if severity_filter != 'all':
        query = query.filter_by(severity=severity_filter)
    
    observations = query.order_by(SafetyObservation.observation_date.desc()).all()
    
    return render_template('projects/safety/observations/list.html',
                          project=project, observations=observations)

@safety_bp.route('/observations/create', methods=['GET', 'POST'])
@login_required
@project_access_required
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
            corrective_action=form.corrective_action.data,
            due_date=form.due_date.data,
            observed_by=current_user.id,
            created_by=current_user.id
        )
        
        db.session.add(observation)
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/observations/{observation.id}')
                    
                    safety_photo = SafetyPhoto(
                        record_type='observation',
                        record_id=observation.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(safety_photo)
            
            db.session.commit()
        
        flash('Safety observation created successfully.', 'success')
        return redirect(url_for('projects.safety.observations', project_id=project_id))
    
    return render_template('projects/safety/observations/create.html', form=form, project=project)

@safety_bp.route('/observations/<int:observation_id>')
@login_required
@project_access_required
def view_observation(observation_id):
    """View a specific safety observation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    observation = SafetyObservation.query.filter_by(
        id=observation_id, project_id=project_id).first_or_404()
    
    photos = SafetyPhoto.query.filter_by(
        record_type='observation', record_id=observation_id).all()
    
    status_form = ObservationStatusForm(obj=observation)
    
    return render_template('projects/safety/observations/view.html',
                          project=project, observation=observation, 
                          photos=photos, status_form=status_form)

@safety_bp.route('/observations/<int:observation_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_observation(observation_id):
    """Edit a safety observation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    observation = SafetyObservation.query.filter_by(
        id=observation_id, project_id=project_id).first_or_404()
    
    form = SafetyObservationForm(obj=observation)
    
    if form.validate_on_submit():
        observation.title = form.title.data
        observation.description = form.description.data
        observation.observation_date = form.observation_date.data
        observation.location = form.location.data
        observation.category = form.category.data
        observation.severity = form.severity.data
        observation.corrective_action = form.corrective_action.data
        observation.due_date = form.due_date.data
        
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/observations/{observation.id}')
                    
                    safety_photo = SafetyPhoto(
                        record_type='observation',
                        record_id=observation.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(safety_photo)
            
            db.session.commit()
        
        flash('Safety observation updated successfully.', 'success')
        return redirect(url_for('projects.safety.view_observation', 
                              project_id=project_id, observation_id=observation_id))
    
    return render_template('projects/safety/observations/edit.html',
                          form=form, project=project, observation=observation)

@safety_bp.route('/observations/<int:observation_id>/update-status', methods=['POST'])
@login_required
@project_access_required
def update_observation_status(observation_id):
    """Update the status of an observation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    observation = SafetyObservation.query.filter_by(
        id=observation_id, project_id=project_id).first_or_404()
    
    form = ObservationStatusForm()
    
    if form.validate_on_submit():
        old_status = observation.status
        new_status = form.status.data
        
        observation.status = new_status
        
        # If setting to closed, record the user & time
        if new_status in ['closed', 'verified'] and old_status != new_status:
            observation.closed_date = datetime.now()
            observation.closed_by = current_user.id
        
        db.session.commit()
        
        flash('Observation status updated successfully.', 'success')
    
    return redirect(url_for('projects.safety.view_observation', 
                          project_id=project_id, observation_id=observation_id))

# Incident Reports routes
@safety_bp.route('/incidents')
@login_required
@project_access_required
def incidents():
    """List all incident reports"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Apply filters if provided
    type_filter = request.args.get('type', 'all')
    severity_filter = request.args.get('severity', 'all')
    
    query = IncidentReport.query.filter_by(project_id=project_id)
    
    if type_filter != 'all':
        query = query.filter_by(incident_type=type_filter)
    
    if severity_filter != 'all':
        query = query.filter_by(severity=severity_filter)
    
    incidents = query.order_by(IncidentReport.incident_date.desc()).all()
    
    return render_template('projects/safety/incidents/list.html',
                          project=project, incidents=incidents)

@safety_bp.route('/incidents/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_incident():
    """Create a new incident report"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = IncidentReportForm()
    
    if form.validate_on_submit():
        # Generate an incident number
        current_year = datetime.now().year
        count = IncidentReport.query.filter_by(project_id=project_id).count() + 1
        incident_number = f"{project.number}-IR-{current_year}-{count:03d}"
        
        incident = IncidentReport(
            project_id=project_id,
            incident_number=incident_number,
            title=form.title.data,
            description=form.description.data,
            incident_date=form.incident_date.data,
            incident_time=form.incident_time.data,
            location=form.location.data,
            incident_type=form.incident_type.data,
            severity=form.severity.data,
            persons_involved=form.persons_involved.data,
            witnesses=form.witnesses.data,
            equipment_involved=form.equipment_involved.data,
            immediate_actions=form.immediate_actions.data,
            weather_conditions=form.weather_conditions.data,
            root_cause=form.root_cause.data,
            corrective_actions=form.corrective_actions.data,
            is_recordable=form.is_recordable.data,
            is_lost_time=form.is_lost_time.data,
            days_lost=form.days_lost.data if form.is_lost_time.data else 0,
            was_reported_to_osha=form.was_reported_to_osha.data,
            osha_report_date=form.osha_report_date.data,
            reported_by=current_user.id
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/incidents/{incident.id}')
                    
                    incident_photo = IncidentPhoto(
                        incident_id=incident.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(incident_photo)
            
            db.session.commit()
        
        flash('Incident report created successfully.', 'success')
        return redirect(url_for('projects.safety.incidents', project_id=project_id))
    
    return render_template('projects/safety/incidents/create.html', 
                          form=form, project=project)

@safety_bp.route('/incidents/<int:incident_id>')
@login_required
@project_access_required
def view_incident(incident_id):
    """View a specific incident report"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    incident = IncidentReport.query.filter_by(
        id=incident_id, project_id=project_id).first_or_404()
    
    photos = IncidentPhoto.query.filter_by(incident_id=incident_id).all()
    
    return render_template('projects/safety/incidents/view.html',
                          project=project, incident=incident, photos=photos)

# JHA routes
@safety_bp.route('/jha')
@login_required
@project_access_required
def jha_list():
    """List all Job Hazard Analyses"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    jhas = JobHazardAnalysis.query.filter_by(project_id=project_id).order_by(
        JobHazardAnalysis.created_date.desc()).all()
    
    return render_template('projects/safety/jha/list.html',
                          project=project, jhas=jhas)

@safety_bp.route('/jha/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_jha():
    """Create a new Job Hazard Analysis"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = JobHazardAnalysisForm()
    
    if request.method == 'GET':
        # Start with one empty step
        form.steps.append_entry()
    
    if form.validate_on_submit():
        # Generate a JHA number
        current_year = datetime.now().year
        count = JobHazardAnalysis.query.filter_by(project_id=project_id).count() + 1
        jha_number = f"{project.number}-JHA-{current_year}-{count:03d}"
        
        jha = JobHazardAnalysis(
            project_id=project_id,
            jha_number=jha_number,
            title=form.title.data,
            description=form.description.data,
            work_area=form.work_area.data,
            equipment_required=form.equipment_required.data,
            ppe_required=form.ppe_required.data,
            training_required=form.training_required.data,
            permits_required=form.permits_required.data,
            emergency_procedures=form.emergency_procedures.data,
            review_date=form.review_date.data,
            created_by=current_user.id
        )
        
        db.session.add(jha)
        db.session.flush()  # Get an ID for the JHA
        
        # Add all steps
        for i, step_form in enumerate(form.steps):
            step = JHAStep(
                jha_id=jha.id,
                step_number=i+1,
                task_description=step_form.task_description.data,
                hazards=step_form.hazards.data,
                controls=step_form.controls.data
            )
            db.session.add(step)
        
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/jha/{jha.id}')
                    
                    safety_photo = SafetyPhoto(
                        record_type='jha',
                        record_id=jha.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(safety_photo)
            
            db.session.commit()
        
        flash('Job Hazard Analysis created successfully.', 'success')
        return redirect(url_for('projects.safety.jha_list', project_id=project_id))
    
    return render_template('projects/safety/jha/create.html', 
                          form=form, project=project)

@safety_bp.route('/jha/<int:jha_id>')
@login_required
@project_access_required
def view_jha(jha_id):
    """View a specific JHA"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    jha = JobHazardAnalysis.query.filter_by(
        id=jha_id, project_id=project_id).first_or_404()
    
    steps = JHAStep.query.filter_by(jha_id=jha_id).order_by(JHAStep.step_number).all()
    photos = SafetyPhoto.query.filter_by(record_type='jha', record_id=jha_id).all()
    
    return render_template('projects/safety/jha/view.html',
                          project=project, jha=jha, steps=steps, photos=photos)

# Pre-Task Plans routes
@safety_bp.route('/pretask')
@login_required
@project_access_required
def pretask():
    """List all Pre-Task Plans"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    plans = PreTaskPlan.query.filter_by(project_id=project_id).order_by(
        PreTaskPlan.plan_date.desc()).all()
    
    return render_template('projects/safety/pretask/list.html',
                          project=project, plans=plans)

@safety_bp.route('/pretask/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_pretask():
    """Create a new Pre-Task Plan"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = PreTaskPlanForm()
    
    if request.method == 'GET':
        # Start with one empty attendee
        form.attendees.append_entry()
    
    if form.validate_on_submit():
        plan = PreTaskPlan(
            project_id=project_id,
            plan_date=form.plan_date.data,
            work_area=form.work_area.data,
            task_description=form.task_description.data,
            company=form.company.data,
            foreman=form.foreman.data,
            equipment_required=form.equipment_required.data,
            ppe_required=form.ppe_required.data,
            potential_hazards=form.potential_hazards.data,
            hazard_controls=form.hazard_controls.data,
            special_precautions=form.special_precautions.data,
            emergency_procedures=form.emergency_procedures.data,
            permits_required=form.permits_required.data,
            safety_equipment=form.safety_equipment.data,
            risk_level=form.risk_level.data,
            created_by=current_user.id
        )
        
        db.session.add(plan)
        db.session.flush()  # Get an ID for the plan
        
        # Add all attendees
        for attendee_form in form.attendees:
            attendee = PreTaskAttendee(
                plan_id=plan.id,
                name=attendee_form.name.data,
                company=attendee_form.company.data,
                signature=attendee_form.signature.data
            )
            db.session.add(attendee)
        
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/pretask/{plan.id}')
                    
                    safety_photo = SafetyPhoto(
                        record_type='pretask',
                        record_id=plan.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(safety_photo)
            
            db.session.commit()
        
        flash('Pre-Task Plan created successfully.', 'success')
        return redirect(url_for('projects.safety.pretask', project_id=project_id))
    
    return render_template('projects/safety/pretask/create.html', 
                          form=form, project=project)

@safety_bp.route('/pretask/<int:plan_id>')
@login_required
@project_access_required
def view_pretask(plan_id):
    """View a specific Pre-Task Plan"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    plan = PreTaskPlan.query.filter_by(
        id=plan_id, project_id=project_id).first_or_404()
    
    attendees = PreTaskAttendee.query.filter_by(plan_id=plan_id).all()
    photos = SafetyPhoto.query.filter_by(record_type='pretask', record_id=plan_id).all()
    
    return render_template('projects/safety/pretask/view.html',
                          project=project, plan=plan, attendees=attendees, photos=photos)

# Safety Orientations routes
@safety_bp.route('/orientations')
@login_required
@project_access_required
def orientations():
    """List all Safety Orientations"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    orientations = SafetyOrientation.query.filter_by(project_id=project_id).order_by(
        SafetyOrientation.orientation_date.desc()).all()
    
    return render_template('projects/safety/orientations/list.html',
                          project=project, orientations=orientations)

@safety_bp.route('/orientations/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_orientation():
    """Create a new Safety Orientation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = SafetyOrientationForm()
    
    if request.method == 'GET':
        # Start with one empty attendee
        form.attendees.append_entry()
    
    if form.validate_on_submit():
        orientation = SafetyOrientation(
            project_id=project_id,
            orientation_date=form.orientation_date.data,
            location=form.location.data,
            trainer=form.trainer.data,
            company=form.company.data,
            topics_covered=form.topics_covered.data,
            created_by=current_user.id
        )
        
        db.session.add(orientation)
        db.session.flush()  # Get an ID for the orientation
        
        # Add all attendees
        for attendee_form in form.attendees:
            attendee = OrientationAttendee(
                orientation_id=orientation.id,
                name=attendee_form.name.data,
                company=attendee_form.company.data,
                position=attendee_form.position.data,
                signature=attendee_form.signature.data
            )
            db.session.add(attendee)
        
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/orientations/{orientation.id}')
                    
                    safety_photo = SafetyPhoto(
                        record_type='orientation',
                        record_id=orientation.id,
                        file_name=photo.filename,
                        file_path=filename,
                        uploaded_by=current_user.id
                    )
                    db.session.add(safety_photo)
            
            db.session.commit()
        
        flash('Safety Orientation created successfully.', 'success')
        return redirect(url_for('projects.safety.orientations', project_id=project_id))
    
    return render_template('projects/safety/orientations/create.html', 
                          form=form, project=project)

@safety_bp.route('/orientations/<int:orientation_id>')
@login_required
@project_access_required
def view_orientation(orientation_id):
    """View a specific Safety Orientation"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    orientation = SafetyOrientation.query.filter_by(
        id=orientation_id, project_id=project_id).first_or_404()
    
    attendees = OrientationAttendee.query.filter_by(orientation_id=orientation_id).all()
    photos = SafetyPhoto.query.filter_by(record_type='orientation', record_id=orientation_id).all()
    
    return render_template('projects/safety/orientations/view.html',
                          project=project, orientation=orientation, 
                          attendees=attendees, photos=photos)

# Safety Metrics routes
@safety_bp.route('/metrics')
@login_required
@project_access_required
def metrics():
    """View safety metrics"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    metrics = SafetyMetrics.query.filter_by(project_id=project_id).order_by(
        SafetyMetrics.date.desc()).all()
    
    # Calculate overall metrics
    total_hours = sum(metric.man_hours for metric in metrics) if metrics else 0
    total_recordables = sum(metric.recordable_incidents for metric in metrics) if metrics else 0
    total_lost_time = sum(metric.lost_time_incidents for metric in metrics) if metrics else 0
    
    trir = (total_recordables * 200000) / total_hours if total_hours > 0 else 0
    ltir = (total_lost_time * 200000) / total_hours if total_hours > 0 else 0
    
    return render_template('projects/safety/metrics.html',
                          project=project, metrics=metrics, 
                          trir=trir, ltir=ltir,
                          total_hours=total_hours,
                          total_recordables=total_recordables,
                          total_lost_time=total_lost_time)

@safety_bp.route('/metrics/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_metrics():
    """Create new safety metrics"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = SafetyMetricsForm()
    
    if form.validate_on_submit():
        # Set the date to the first day of the month
        metric_date = form.date.data.replace(day=1)
        
        # Check if metrics already exist for this month
        existing = SafetyMetrics.query.filter_by(
            project_id=project_id,
            date=metric_date
        ).first()
        
        if existing:
            flash('Metrics for this month already exist. Please edit the existing record.', 'warning')
            return redirect(url_for('projects.safety.edit_metrics', 
                                  project_id=project_id, metric_id=existing.id))
        
        # Create new metrics
        metrics = SafetyMetrics(
            project_id=project_id,
            date=metric_date,
            man_hours=form.man_hours.data,
            recordable_incidents=form.recordable_incidents.data,
            lost_time_incidents=form.lost_time_incidents.data,
            near_misses=form.near_misses.data,
            first_aid_cases=form.first_aid_cases.data,
            property_damage_incidents=form.