
# app/projects/field/routes.
from . import field_bp
from werkzeug.utils import secure_filename
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.field import (
    DailyReport, ProjectPhoto, SafetyIncident, PunchlistItem,
    LaborEntry, EquipmentEntry, WeatherCondition, WorkStatus
)
from datetime import datetime 
from app.projects.field.forms import (
    DailyReportForm, ProjectPhotoForm, SafetyIncidentForm,
    PunchlistItemForm, PunchlistStatusForm
)
from app.extensions import db
from app.utils.access_control import project_access_required, has_project_access
from app.utils.file_upload import save_file
from datetime import datetime, timedelta
import os

@field_bp.route('/<int:project_id>/field')
@login_required
@project_access_required
def index(project_id):
    """Field dashboard for a project"""
    # Log that we're entering this route
    current_app.logger.info(f"Accessing field index for project {project_id}")
    
    # This will be called after project_access_required has verified access
    project = Project.query.get_or_404(project_id)
    
    # Get counts for widgets
    try:
        daily_reports_count = DailyReport.query.filter_by(project_id=project_id).count()
    except Exception as e:
        current_app.logger.error(f"Error getting daily reports count: {str(e)}")
        daily_reports_count = 0
        
    try:
        photos_count = ProjectPhoto.query.filter_by(project_id=project_id).count()
    except Exception as e:
        current_app.logger.error(f"Error getting photos count: {str(e)}")
        photos_count = 0
        
    try:
        safety_incidents_count = SafetyIncident.query.filter_by(project_id=project_id).count()
    except Exception as e:
        current_app.logger.error(f"Error getting safety incidents count: {str(e)}")
        safety_incidents_count = 0
    
    # Get recent reports (last 5)
    try:
        recent_reports = DailyReport.query.filter_by(project_id=project_id)\
            .order_by(DailyReport.report_date.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(f"Error getting recent reports: {str(e)}")
        recent_reports = []
    
    # Get recent photos (last 8)
    try:
        recent_photos = ProjectPhoto.query.filter_by(project_id=project_id)\
            .order_by(ProjectPhoto.uploaded_at.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(f"Error getting recent photos: {str(e)}")
        recent_photos = []
    
    # Get overdue punchlist items
    try:
        today = datetime.utcnow().date()
        overdue_items = PunchlistItem.query.filter_by(project_id=project_id)\
            .filter(PunchlistItem.due_date < today)\
            .filter(PunchlistItem.status.in_(['open', 'in_progress']))\
            .order_by(PunchlistItem.due_date.asc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(f"Error getting overdue items: {str(e)}")
        overdue_items = []
        today = datetime.utcnow().date()
    
    # Calculate project completion percentage (placeholder logic)
    project_completion = 40  # Placeholder value
    
    # Log that we're about to render the template
    current_app.logger.info(f"Rendering field dashboard for project {project_id}")
    
    # Return the template with all variables
    return render_template('projects/field/dashboard.html',
                          project=project,
                          daily_reports_count=daily_reports_count,
                          photos_count=photos_count,
                          safety_incidents_count=safety_incidents_count,
                          recent_reports=recent_reports,
                          recent_photos=recent_photos,
                          overdue_items=overdue_items,
                          project_completion=project_completion,
                          today=today)


@field_bp.route('/<int:project_id>/daily-reports')
@login_required
@project_access_required
def daily_reports(project_id):
    """List all daily reports for a project"""
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        reports = DailyReport.query.filter_by(project_id=project_id)\
            .order_by(DailyReport.report_date.desc())\
            .paginate(page=page, per_page=per_page)
    except Exception as e:
        current_app.logger.error(f"Error getting daily reports: {str(e)}")
        reports = None
    
    return render_template('projects/field/daily_reports/index.html',
                          project=project, reports=reports)
@field_bp.route('/<int:project_id>/daily-reports/create', methods=['GET', 'POST'])
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
        try:
            # Create the daily report object
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
                work_performed=form.work_summary.data,  # Map work_summary to work_performed
                materials_received=form.materials_received.data,
                issues=form.issues.data,
                notes=form.notes.data,
                created_by=current_user.id
            )
            
            # First commit the report to get its ID
            db.session.add(report)
            db.session.commit()
            
            # Now add labor entries using the report ID
            for entry_data in form.labor_entries.data:
                labor_entry = LaborEntry(
                    daily_report_id=report.id,  # Now we have the report.id
                    company=entry_data['company'],
                    work_description=entry_data['work_description'],
                    worker_count=entry_data['worker_count'],
                    hours_worked=entry_data['hours_worked']
                )
                db.session.add(labor_entry)
            
            # Add equipment entries using the report ID
            for entry_data in form.equipment_entries.data:
                equipment_entry = EquipmentEntry(
                    daily_report_id=report.id,  # Now we have the report.id
                    equipment_type=entry_data['equipment_type'],
                    count=entry_data['count'],
                    hours_used=entry_data['hours_used'],
                    notes=entry_data.get('notes', '')  # Use get with default value
                )
                db.session.add(equipment_entry)
            
            # Process photos if any - use request.files instead of form.photos.data
            if 'photos' in request.files:
                photos = request.files.getlist('photos')
                for photo in photos:
                    if photo.filename:
                        filename = save_file(photo, folder=f'projects/{project_id}/daily_reports/{report.id}')
                        
                        # Get file size
                        photo.seek(0)
                        file_size = len(photo.read())
                        
                        project_photo = ProjectPhoto(
                            project_id=project_id,
                            daily_report_id=report.id,
                            title=f"Daily Report Photo - {report.report_date}",
                            file_path=filename,
                            file_size=file_size,
                            uploaded_by=current_user.id
                        )
                        db.session.add(project_photo)
            
            # Commit again to save entries and photos
            db.session.commit()
            
            flash('Daily report created successfully!', 'success')
            return redirect(url_for('projects_field.daily_reports', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating daily report: {str(e)}")
            flash(f"Error creating daily report: {str(e)}", "danger")
    
    return render_template('projects/field/daily_reports/create.html',
                          project=project, form=form)

@field_bp.route('<int:project_id>/field/daily-reports/<int:report_id>/view')
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

@field_bp.route('/<int:project_id>/field/daily-reports/<int:report_id>/edit', methods=['GET', 'POST'])
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
@field_bp.route('/<int:project_id>/daily-reports/<int:report_id>/submit', methods=['POST'])
@login_required
@project_access_required
def submit_report(project_id, report_id):
    """Submit a daily report"""
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Check if the report is already submitted
    if report.is_submitted:
        flash('This report has already been submitted.', 'info')
    else:
        # Update report status
        report.is_submitted = True
        report.submitted_at = datetime.utcnow()
        db.session.commit()
        flash('Daily report has been submitted successfully.', 'success')
    
    return redirect(url_for('projects_field.view_daily_report', project_id=project_id, report_id=report_id))


@field_bp.route('/<int:project_id>/daily-reports/<int:report_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_daily_report(project_id, report_id):
    """Delete a daily report"""
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Check if user has permission to delete
    if not current_user.is_admin() and current_user.id != report.created_by:
        flash('You do not have permission to delete this report.', 'danger')
        return redirect(url_for('projects_field.view_daily_report', project_id=project_id, report_id=report_id))
    
    # Delete associated labor and equipment entries (assuming cascading is not set)
    LaborEntry.query.filter_by(daily_report_id=report.id).delete()
    EquipmentEntry.query.filter_by(daily_report_id=report.id).delete()
    
    # Delete the report
    db.session.delete(report)
    db.session.commit()
    
    flash('Daily report has been deleted successfully.', 'success')
    return redirect(url_for('projects_field.daily_reports', project_id=project_id))
    
@field_bp.route('/<int:project_id>/photos')
@login_required
def photos(project_id):
    """List all photos for a project"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 24, type=int)
    
    try:
        photos = ProjectPhoto.query.filter_by(project_id=project_id)\
            .order_by(ProjectPhoto.uploaded_at.desc())\
            .paginate(page=page, per_page=per_page)
        if photos and photos.items:
            for photo in photos.items:
                current_app.logger.debug(f"Photo file path: {photo.file_path}")
    except:
        photos = None
    
    return render_template('projects/field/photos/index.html',
                          project=project, photos=photos)

@field_bp.route('/<int:project_id>/field/photos/upload', methods=['GET', 'POST'])
@login_required
@project_access_required
def upload_photo(project_id):
    """Upload a new photo"""
    project = Project.query.get_or_404(project_id)
    form = ProjectPhotoForm()
    
    if form.validate_on_submit():
        try:
            # Make sure to seek to the beginning of the file before saving
            form.photo.data.seek(0)
            
            # Save file and get the path relative to static folder
            relative_path = save_file(form.photo.data, folder=f'projects/{project_id}/photos')
            
            # Get file size
            form.photo.data.seek(0)
            file_size = len(form.photo.data.read())
            
            # Create and save the photo record
            photo = ProjectPhoto(
                project_id=project_id,
                title=form.title.data,
                description=form.description.data,
                location=form.location.data,
                file_path=relative_path,  # This should be relative to the static folder
                file_size=file_size,
                is_featured=form.is_featured.data,
                uploaded_by=current_user.id
            )
            
            db.session.add(photo)
            db.session.commit()
            
            flash('Photo uploaded successfully.', 'success')
            return redirect(url_for('projects_field.photos', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading photo: {str(e)}")
            flash(f"Error uploading photo: {str(e)}", "danger")
    
    return render_template('projects/field/photos/upload.html',
                          project=project, form=form)
def save_file(file, folder=''):
    """Save a file to the uploads directory"""
    from werkzeug.utils import secure_filename
    import os
    import uuid
    from flask import current_app
    
    filename = secure_filename(file.filename)
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Normalize the folder path to use forward slashes consistently
    folder = folder.replace('\\', '/')
    
    # Create physical path for storage
    upload_path = os.path.join(current_app.static_folder, 'uploads', folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    # Create and return a web-friendly path with forward slashes
    # This is critical for correct URL generation
    relative_path = f"uploads/{folder}/{unique_filename}"
    relative_path = relative_path.replace('\\', '/')
    
    return relative_path
# Safety Incidents routes

@field_bp.route('/<int:project_id>/safety')
@login_required
def safety_incidents(project_id):
    """List all safety incidents for a project"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        incidents = SafetyIncident.query.filter_by(project_id=project_id)\
            .order_by(SafetyIncident.incident_date.desc())\
            .paginate(page=page, per_page=per_page)
    except:
        incidents = None
    
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

@field_bp.route('/<int:project_id>/punchlist')
@login_required
def punchlists(project_id):
    """List all punchlist items for a project"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        query = PunchlistItem.query.filter_by(project_id=project_id)
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        items = query.order_by(PunchlistItem.due_date.asc()).paginate(page=page, per_page=per_page)
    except:
        items = None
    
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

@field_bp.route('/<int:project_id>/daily-reports/<int:report_id>/pdf')
@login_required
@project_access_required
def daily_report_pdf(project_id, report_id):
    """Generate PDF version of a daily report"""
    from datetime import datetime  # Make sure this import is at the top of your file
    
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Get photos associated with this report
    photos = ProjectPhoto.query.filter_by(daily_report_id=report_id).all()
    
    # Calculate totals for labor and equipment
    total_workers = db.session.query(db.func.sum(LaborEntry.worker_count)).filter(LaborEntry.daily_report_id == report.id).scalar() or 0
    
    # Calculate total man-hours
    total_man_hours = 0
    for entry in report.labor_entries:
        total_man_hours += entry.worker_count * entry.hours_worked
    
    # Calculate equipment totals
    total_equipment = db.session.query(db.func.sum(EquipmentEntry.count)).filter(EquipmentEntry.daily_report_id == report.id).scalar() or 0
    total_equipment_hours = db.session.query(db.func.sum(EquipmentEntry.hours_used)).filter(EquipmentEntry.daily_report_id == report.id).scalar() or 0
    
    try:
        # Import PDF generation tools
        from flask import make_response
        from weasyprint import HTML, CSS
        from io import BytesIO
        
        # Render the template to HTML
        html = render_template('projects/field/daily_reports/pdf_template.html',
                              project=project, 
                              report=report, 
                              photos=photos,
                              total_workers=total_workers,
                              total_man_hours=total_man_hours,
                              total_equipment=total_equipment,
                              total_equipment_hours=total_equipment_hours,
                              datetime=datetime)  # Add this line to pass the datetime module
        
        # Generate PDF from HTML
        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        # Create response
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=daily_report_{report.report_number}.pdf'
        
        return response
    except ImportError:
        # If PDF generation libraries are not available, return a message
        flash('PDF generation is not available. Please install WeasyPrint.', 'warning')
        return redirect(url_for('projects_field.view_daily_report', project_id=project_id, report_id=report_id))
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('projects_field.view_daily_report', project_id=project_id, report_id=report_id))
    

@field_bp.route('/<int:project_id>/daily-reports/<int:report_id>/print')
@login_required
@project_access_required
def daily_report_print(project_id, report_id):
    """Print-friendly version of a daily report"""
    from datetime import datetime
    
    project = Project.query.get_or_404(project_id)
    report = DailyReport.query.filter_by(id=report_id, project_id=project_id).first_or_404()
    
    # Get photos associated with this report
    photos = ProjectPhoto.query.filter_by(daily_report_id=report_id).all()
    
    # Calculate totals
    total_workers = db.session.query(db.func.sum(LaborEntry.worker_count)).filter(LaborEntry.daily_report_id == report.id).scalar() or 0
    
    # Calculate total man-hours
    total_man_hours = 0
    for entry in report.labor_entries:
        total_man_hours += entry.worker_count * entry.hours_worked
    
    # Calculate equipment totals
    total_equipment = db.session.query(db.func.sum(EquipmentEntry.count)).filter(EquipmentEntry.daily_report_id == report.id).scalar() or 0
    total_equipment_hours = db.session.query(db.func.sum(EquipmentEntry.hours_used)).filter(EquipmentEntry.daily_report_id == report.id).scalar() or 0
    
    return render_template('projects/field/daily_reports/pdf_template.html',
                          project=project, 
                          report=report, 
                          photos=photos,
                          total_workers=total_workers,
                          total_man_hours=total_man_hours,
                          total_equipment=total_equipment,
                          total_equipment_hours=total_equipment_hours,
                          datetime=datetime)