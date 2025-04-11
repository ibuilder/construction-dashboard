from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.field import (
    DailyReport, ProjectPhoto, SafetyIncident, PunchlistItem,
    LaborEntry, EquipmentEntry, WeatherCondition, WorkStatus
)
from app.projects.field.forms import (
    DailyReportForm, ProjectPhotoForm, SafetyIncidentForm,
    PunchlistItemForm, PunchlistStatusForm
)
from app.extensions import db
from app.utils.permissions import project_access_required
from app.utils.file_upload import save_file
from datetime import datetime, timedelta
import os

field_bp = Blueprint('projects.field', __name__)

@field_bp.route('/projects/<int:project_id>/field')
@login_required
@project_access_required
def dashboard(project_id):
    """Field dashboard for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Get counts for widgets
    daily_reports_count = DailyReport.query.filter_by(project_id=project_id).count()
    photos_count = ProjectPhoto.query.filter_by(project_id=project_id).count()
    safety_incidents_count = SafetyIncident.query.filter_by(project_id=project_id).count()
    
    # Get recent reports (last 5)
    recent_reports = DailyReport.query.filter_by(project_id=project_id)\
        .order_by(DailyReport.report_date.desc()).limit(5).all()
    
    # Get recent photos (last 8)
    recent_photos = ProjectPhoto.query.filter_by(project_id=project_id)\
        .order_by(ProjectPhoto.uploaded_at.desc()).limit(8).all()
    
    # Get overdue punchlist items
    today = datetime.utcnow().date()
    overdue_items = PunchlistItem.query.filter_by(project_id=project_id)\
        .filter(PunchlistItem.due_date < today)\
        .filter(PunchlistItem.status.in_(['open', 'in_progress']))\
        .order_by(PunchlistItem.due_date.asc()).limit(5).all()
    
    # Calculate project completion percentage (placeholder logic)
    # This would normally come from a more sophisticated calculation
    project_completion = 40  # Placeholder value
    
    return render_template('projects/field/dashboard.html',
                          project=project,
                          daily_reports_count=daily_reports_count,
                          photos_count=photos_count,
                          safety_incidents_count=safety_incidents_count,
                          recent_reports=recent_reports,
                          recent_photos=recent_photos,
                          overdue_items=overdue_items,
                          project_completion=project_completion)

# Daily Reports routes

@field_bp.route('/projects/<int:project_id>/field/daily-reports')
@login_required
@project_access_required
def daily_reports(project_id):
    """List all daily reports for a project"""
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    reports = DailyReport.query.filter_by(project_id=project_id)\
        .order_by(DailyReport.report_date.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('projects/field/daily_reports/index.html',
                          project=project, reports=reports)

@field_bp.route('/projects/<int:project_id>/field/daily-reports/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_daily_report(project_id):
    """Create a new daily report"""
    project = Project.query.get_or_404(project_id)
    form = DailyReportForm()
    
    # Auto-generate report number based on date and project
    if request.method == 'GET':
        today = datetime.utcnow().date()
        count = DailyReport.query.filter_by(project_id=project_id).count() + 1
        form.report_number.data = f"{project.number}-DR-{today.strftime('%Y%m%d')}-{count}"
    
    if form.validate_on_submit():
        report = DailyReport(
            project_id=project_id,
            report_number=form.report_number.data,
            report_date=form.report_date.data,
            weather_condition=form.weather_condition.data,
            temperature_low=form.temperature_low.data,
            temperature_high=form.temperature_high.data,
            precipitation=form.precipitation.data,
            wind_speed=form.wind_speed.data,
            site_conditions=form.site_conditions.data,
            work_status=form.work_status.data,
            delay_reason=form.delay_reason.data,
            work_performed=form.work_performed.data,
            materials_received=form.materials_received.data,
            issues=form.issues.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Add labor entries
        for entry_data in form.labor_entries.data:
            labor_entry = LaborEntry(
                company=entry_data['company'],
                work_description=entry_data['work_description'],
                worker_count=entry_data['worker_count'],
                hours_worked=entry_data['hours_worked']
            )
            report.labor_entries.append(labor_entry)
        
        # Add equipment entries
        for entry_data in form.equipment_entries.data:
            equipment_entry = EquipmentEntry(
                equipment_type=entry_data['equipment_type'],
                count=entry_data['count'],
                hours_used=entry_data['hours_used'],
                notes=entry_data['notes']
            )
            report.equipment_entries.append(equipment_entry)
        
        # Save report
        db.session.add(report)
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/daily_reports/{report.id}')
                    
                    project_photo = ProjectPhoto(
                        project_id=project_id,
                        daily_report_id=report.id,
                        title=f"Daily Report Photo - {report.report_date}",
                        file_path=filename,
                        file_size=len(photo.read()),
                        uploaded_by=current_user.id
                    )
                    db.session.add(project_photo)
            
            db.session.commit()
        
        # Check if submitting final report or saving draft
        if form.submit_report.data:
            report.is_submitted = True
            report.submitted_at = datetime.utcnow()
            db.session.commit()
            flash('Daily report has been submitted successfully.', 'success')
        else:
            flash('Daily report has been saved as draft.', 'success')
        
        return redirect(url_for('projects.field.view_daily_report', project_id=project_id, report_id=report.id))
    
    return render_template('projects/field/daily_reports/create.html',
                          project=project, form=form)

@field_bp.route('/projects/<int:project_id>/field/daily-reports/<int:report_id>')
@login_required
@project_access_required
def view_daily_report(project_id, report_id):
    """View a single daily report"""
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Get photos associated with this report
    photos = ProjectPhoto.query.filter_by(daily_report_id=report_id).all()
    
    return render_template('projects/field/daily_reports/view.html',
                          project=project, report=report, photos=photos)

@field_bp.route('/projects/<int:project_id>/field/daily-reports/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_daily_report(project_id, report_id):
    """Edit an existing daily report"""
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Check if report is already submitted
    if report.is_submitted and not current_user.is_admin():
        flash('Cannot edit a submitted report.', 'danger')
        return redirect(url_for('projects.field.view_daily_report', project_id=project_id, report_id=report_id))
    
    form = DailyReportForm(obj=report)
    
    if request.method == 'GET':
        # Populate form with existing labor entries
        form.labor_entries.entries = []
        for entry in report.labor_entries:
            form.labor_entries.append_entry({
                'company': entry.company,
                'work_description': entry.work_description,
                'worker_count': entry.worker_count,
                'hours_worked': entry.hours_worked
            })
        
        # Populate form with existing equipment entries
        form.equipment_entries.entries = []
        for entry in report.equipment_entries:
            form.equipment_entries.append_entry({
                'equipment_type': entry.equipment_type,
                'count': entry.count,
                'hours_used': entry.hours_used,
                'notes': entry.notes
            })
    
    if form.validate_on_submit():
        # Update report fields
        form.populate_obj(report)
        
        # Update is_submitted status
        if form.submit_report.data and not report.is_submitted:
            report.is_submitted = True
            report.submitted_at = datetime.utcnow()
            flash_message = 'Daily report has been submitted successfully.'
        else:
            flash_message = 'Daily report has been updated successfully.'
        
        # Clear existing entries and add new ones
        LaborEntry.query.filter_by(daily_report_id=report.id).delete()
        EquipmentEntry.query.filter_by(daily_report_id=report.id).delete()
        
        # Add labor entries
        for entry_data in form.labor_entries.data:
            labor_entry = LaborEntry(
                daily_report_id=report.id,
                company=entry_data['company'],
                work_description=entry_data['work_description'],
                worker_count=entry_data['worker_count'],
                hours_worked=entry_data['hours_worked']
            )
            db.session.add(labor_entry)
        
        # Add equipment entries
        for entry_data in form.equipment_entries.data:
            equipment_entry = EquipmentEntry(
                daily_report_id=report.id,
                equipment_type=entry_data['equipment_type'],
                count=entry_data['count'],
                hours_used=entry_data['hours_used'],
                notes=entry_data['notes']
            )
            db.session.add(equipment_entry)
        
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/daily_reports/{report.id}')
                    
                    project_photo = ProjectPhoto(
                        project_id=project_id,
                        daily_report_id=report.id,
                        title=f"Daily Report Photo - {report.report_date}",
                        file_path=filename,
                        file_size=len(photo.read()),
                        uploaded_by=current_user.id
                    )
                    db.session.add(project_photo)
            
            db.session.commit()
        
        flash(flash_message, 'success')
        return redirect(url_for('projects.field.view_daily_report', project_id=project_id, report_id=report.id))
    
    return render_template('projects/field/daily_reports/edit.html',
                          project=project, report=report, form=form)

# Photos routes

@field_bp.route('/projects/<int:project_id>/field/photos')
@login_required
@project_access_required
def photos(project_id):
    """List all photos for a project"""
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 24, type=int)
    
    photos = ProjectPhoto.query.filter_by(project_id=project_id)\
        .order_by(ProjectPhoto.uploaded_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('projects/field/photos/index.html',
                          project=project, photos=photos)

@field_bp.route('/projects/<int:project_id>/field/photos/upload', methods=['GET', 'POST'])
@login_required
@project_access_required
def upload_photo(project_id):
    """Upload a new photo"""
    project = Project.query.get_or_404(project_id)
    form = ProjectPhotoForm()
    
    if form.validate_on_submit():
        filename = save_file(form.photo.data, folder=f'projects/{project_id}/photos')
        
        photo = ProjectPhoto(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            file_path=filename,
            file_size=len(form.photo.data.read()),
            is_featured=form.is_featured.data,
            uploaded_by=current_user.id
        )
        
        db.session.add(photo)
        db.session.commit()
        
        flash('Photo uploaded successfully.', 'success')
        return redirect(url_for('projects.field.photos', project_id=project_id))
    
    return render_template('projects/field/photos/upload.html',
                          project=project, form=form)

# Safety Incidents routes

@field_bp.route('/projects/<int:project_id>/field/safety')
@login_required
@project_access_required
def safety_incidents(project_id):
    """List all safety incidents for a project"""
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    incidents = SafetyIncident.query.filter_by(project_id=project_id)\
        .order_by(SafetyIncident.incident_date.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('projects/field/safety/index.html',
                          project=project, incidents=incidents)

@field_bp.route('/projects/<int:project_id>/field/safety/report', methods=['GET', 'POST'])
@login_required
@project_access_required
def report_safety_incident(project_id):
    """Report a new safety incident"""
    project = Project.query.get_or_404(project_id)
    form = SafetyIncidentForm()
    
    if form.validate_on_submit():
        incident = SafetyIncident(
            project_id=project_id,
            incident_date=form.incident_date.data,
            incident_time=form.incident_time.data,
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            severity=form.severity.data,
            type=form.incident_type.data,
            involved_parties=form.involved_parties.data,
            witnesses=form.witnesses.data,
            actions_taken=form.actions_taken.data,
            reported_by=current_user.id
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/safety/{incident.id}')
                    
                    project_photo = ProjectPhoto(
                        project_id=project_id,
                        title=f"Safety Incident - {incident.title}",
                        description=f"Photo for incident reported on {incident.incident_date}",
                        file_path=filename,
                        file_size=len(photo.read()),
                        uploaded_by=current_user.id
                    )
                    db.session.add(project_photo)
            
            db.session.commit()
        
        flash('Safety incident reported successfully.', 'success')
        return redirect(url_for('projects.field.view_safety_incident', project_id=project_id, incident_id=incident.id))
    
    return render_template('projects/field/safety/report.html',
                          project=project, form=form)

@field_bp.route('/projects/<int:project_id>/field/safety/<int:incident_id>')
@login_required
@project_access_required
def view_safety_incident(project_id, incident_id):
    """View a single safety incident"""
    project = Project.query.get_or_404(project_id)
    incident = SafetyIncident.query.filter_by(id=incident_id, project_id=project_id).first_or_404()
    
    return render_template('projects/field/safety/view.html',
                          project=project, incident=incident)

# Punchlist routes

@field_bp.route('/projects/<int:project_id>/field/punchlist')
@login_required
@project_access_required
def punchlists(project_id):
    """List all punchlist items for a project"""
    project = Project.query.get_or_404(project_id)
    
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PunchlistItem.query.filter_by(project_id=project_id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    items = query.order_by(PunchlistItem.due_date.asc()).paginate(page=page, per_page=per_page)
    
    return render_template('projects/field/punchlist/index.html',
                          project=project, items=items, status_filter=status_filter)

@field_bp.route('/projects/<int:project_id>/field/punchlist/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_punchlist_item(project_id):
    """Create a new punchlist item"""
    project = Project.query.get_or_404(project_id)
    form = PunchlistItemForm()
    
    if form.validate_on_submit():
        item = PunchlistItem(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            category=form.category.data,
            responsible_party=form.responsible_party.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            created_by=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Process photos if any
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                if photo.filename:
                    filename = save_file(photo, folder=f'projects/{project_id}/punchlist/{item.id}')
                    
                    project_photo = ProjectPhoto(
                        project_id=project_id,
                        title=f"Punchlist Item - {item.title}",
                        description=f"Photo for punchlist item: {item.title}",
                        file_path=filename,
                        file_size=len(photo.read()),
                        uploaded_by=current_user.id
                    )
                    db.session.add(project_photo)
            
            db.session.commit()
        
        flash('Punchlist item created successfully.', 'success')
        return redirect(url_for('projects.field.view_punchlist', project_id=project_id, item_id=item.id))
    
    return render_template('projects/field/punchlist/create.html',
                          project=project, form=form)

@field_bp.route('/projects/<int:project_id>/field/punchlist/<int:item_id>')
@login_required
@project_access_required
def view_punchlist(project_id, item_id):
    """View a single punchlist item"""
    project = Project.query.get_or_404(project_id)
    item = PunchlistItem.query.filter_by(id=item_id, project_id=project_id).first_or_404()
    
    status_form = PunchlistStatusForm(obj=item)
    
    return render_template('projects/field/punchlist/view.html',
                          project=project, item=item, status_form=status_form)

@field_bp.route('/projects/<int:project_id>/field/punchlist/<int:item_id>/status', methods=['POST'])
@login_required
@project_access_required
def update_punchlist_status(project_id, item_id):
    """Update the status of a punchlist item"""
    project = Project.query.get_or_404(project_id)
    item = PunchlistItem.query.filter_by(id=item_id, project_id=project_id).first_or_404()
    
    form = PunchlistStatusForm()
    
    if form.validate_on_submit():
        old_status = item.status
        new_status = form.status.data
        
        # Update the status
        item.status = new_status
        
        # Update timestamp fields based on status
        if new_status == 'completed' and old_status != 'completed':
            item.completed_at = datetime.utcnow()
            item.completed_by = current_user.id
        elif new_status == 'verified' and old_status != 'verified':
            item.verified_at = datetime.utcnow()
            item.verified_by = current_user.id
        
        db.session.commit()
        
        flash('Punchlist item status updated successfully.', 'success')
    
    return redirect(url_for('projects.field.view_punchlist', project_id=project_id, item_id=item_id))