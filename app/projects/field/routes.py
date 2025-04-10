from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from . import field_bp
from .forms import DailyReportForm, PhotoForm, PunchlistForm, PunchlistItemForm, ChecklistForm
from app.models.field import DailyReport, Photo, Schedule, Checklist, Punchlist, PullPlan
from app.models.base import Comment, Attachment
from app.models.project import Project
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from datetime import datetime
import os
import uuid

# Field Dashboard
@field_bp.route('/dashboard')
@login_required
def dashboard():
    """Field dashboard with summary of all modules"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get counts and summary data
    daily_reports_count = DailyReport.query.filter_by(project_id=project_id).count()
    photos_count = Photo.query.filter_by(project_id=project_id).count()
    schedules_count = Schedule.query.filter_by(project_id=project_id).count()
    checklists_count = Checklist.query.filter_by(project_id=project_id).count()
    punchlists_count = Punchlist.query.filter_by(project_id=project_id).count()
    pullplans_count = PullPlan.query.filter_by(project_id=project_id).count()
    
    # Latest daily report
    latest_report = DailyReport.query.filter_by(project_id=project_id).order_by(DailyReport.report_date.desc()).first()
    
    # Open punchlist items count
    open_punchlist_items = db.session.query(db.func.count(Punchlist.id)).join(
        Punchlist.items
    ).filter(
        Punchlist.project_id == project_id, 
        Punchlist.items.status == 'open'
    ).scalar() or 0
    
    # Get weather data from latest reports for chart
    weather_data = DailyReport.query.filter_by(
        project_id=project_id
    ).order_by(
        DailyReport.report_date.desc()
    ).limit(7).all()
    
    weather_dates = [report.report_date.strftime('%m/%d') for report in reversed(weather_data)]
    high_temps = [report.temperature_high for report in reversed(weather_data)]
    low_temps = [report.temperature_low for report in reversed(weather_data)]
    
    return render_template('projects/field/dashboard.html',
                          project=project,
                          daily_reports_count=daily_reports_count,
                          photos_count=photos_count,
                          schedules_count=schedules_count,
                          checklists_count=checklists_count,
                          punchlists_count=punchlists_count,
                          pullplans_count=pullplans_count,
                          latest_report=latest_report,
                          open_punchlist_items=open_punchlist_items,
                          weather_dates=weather_dates,
                          high_temps=high_temps,
                          low_temps=low_temps)

# Daily Reports Routes
@field_bp.route('/daily-reports')
@login_required
def daily_reports():
    """List all daily reports for a project"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    reports = DailyReport.query.filter_by(project_id=project_id).order_by(DailyReport.report_date.desc()).all()
    return render_template('projects/field/daily_reports/list.html', 
                          project=project, reports=reports)

@field_bp.route('/daily-reports/create', methods=['GET', 'POST'])
@login_required
def create_daily_report():
    """Create a new daily report"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = DailyReportForm()
    
    # Check if a report already exists for today
    today = datetime.now().date()
    existing_report = DailyReport.query.filter_by(
        project_id=project_id, report_date=today).first()
    
    if existing_report:
        flash('A report for today already exists. You can edit the existing report.', 'warning')
        return redirect(url_for('projects.field.edit_daily_report', id=existing_report.id))
    
    # Get next report number
    last_report = DailyReport.query.filter_by(project_id=project_id).order_by(DailyReport.id.desc()).first()
    next_number = f"DR-{(last_report.id + 1 if last_report else 1):04d}"
    form.report_number.data = next_number
    
    if form.validate_on_submit():
        report = DailyReport(
            project_id=project_id,
            report_date=form.report_date.data or today,
            report_number=form.report_number.data,
            weather_conditions=form.weather_conditions.data,
            temperature_high=form.temperature_high.data,
            temperature_low=form.temperature_low.data,
            precipitation=form.precipitation.data,
            wind_speed=form.wind_speed.data,
            delays=form.delays.data,
            delay_description=form.delay_description.data if form.delays.data else None,
            manpower_count=form.manpower_count.data or 0,
            work_performed=form.work_performed.data,
            materials_received=form.materials_received.data,
            equipment_used=form.equipment_used.data,
            visitors=form.visitors.data,
            safety_incidents=form.safety_incidents.data,
            quality_issues=form.quality_issues.data,
            created_by=current_user.id
        )
        db.session.add(report)
        db.session.commit()
        
        flash('Daily report created successfully!', 'success')
        return redirect(url_for('projects.field.daily_reports', project_id=project_id))
    
    return render_template('projects/field/daily_reports/create.html',
                          project=project, form=form)

@field_bp.route('/daily-reports/<int:id>')
@login_required
def view_daily_report(id):
    """View a specific daily report"""
    report = DailyReport.query.get_or_404(id)
    project = Project.query.get_or_404(report.project_id)
    
    # Get photos associated with this report
    photos = Photo.query.filter_by(daily_report_id=id).all()
    
    # Get comments
    comments = Comment.query.filter_by(record_type='daily_report', record_id=id).order_by(Comment.created_at).all()
    
    # Get attachments
    attachments = Attachment.query.filter_by(record_type='daily_report', record_id=id).all()
    
    return render_template('projects/field/daily_reports/view.html',
                          project=project, report=report,
                          photos=photos, comments=comments,
                          attachments=attachments)

# Implement routes for editing daily reports, photos, punchlist, etc. following
# similar patterns as above modules