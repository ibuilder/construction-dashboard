from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from . import engineering_bp
from .forms import RFIForm, SubmittalForm, DrawingForm, SpecificationForm, PermitForm, MeetingForm, TransmittalForm
from app.models.engineering import RFI, Submittal, Drawing, Specification, Permit, Meeting, Transmittal
from app.models.base import Comment, Attachment
from app.models.project import Project
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from datetime import datetime
import os
import uuid

# Engineering Dashboard
@engineering_bp.route('/dashboard')
@login_required
def dashboard():
    """Engineering dashboard with summary of all modules"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get counts for all engineering modules
    rfi_count = RFI.query.filter_by(project_id=project_id).count()
    submittal_count = Submittal.query.filter_by(project_id=project_id).count()
    drawing_count = Drawing.query.filter_by(project_id=project_id).count()
    spec_count = Specification.query.filter_by(project_id=project_id).count()
    permit_count = Permit.query.filter_by(project_id=project_id).count()
    meeting_count = Meeting.query.filter_by(project_id=project_id).count()
    transmittal_count = Transmittal.query.filter_by(project_id=project_id).count()
    
    # Get RFIs by status for chart
    rfi_by_status = db.session.query(
        RFI.status, db.func.count(RFI.id)
    ).filter_by(project_id=project_id).group_by(RFI.status).all()
    
    # Get submittals by status for chart
    submittals_by_status = db.session.query(
        Submittal.status, db.func.count(Submittal.id)
    ).filter_by(project_id=project_id).group_by(Submittal.status).all()
    
    # Format chart data
    rfi_labels = [status.replace('_', ' ').title() for status, _ in rfi_by_status]
    rfi_data = [count for _, count in rfi_by_status]
    
    submittal_labels = [status.replace('_', ' ').title() for status, _ in submittals_by_status]
    submittal_data = [count for _, count in submittals_by_status]
    
    return render_template('projects/engineering/dashboard.html',
                          project=project,
                          rfi_count=rfi_count,
                          submittal_count=submittal_count,
                          drawing_count=drawing_count,
                          spec_count=spec_count,
                          permit_count=permit_count,
                          meeting_count=meeting_count,
                          transmittal_count=transmittal_count,
                          rfi_labels=rfi_labels,
                          rfi_data=rfi_data,
                          submittal_labels=submittal_labels,
                          submittal_data=submittal_data)

# RFI Routes
@engineering_bp.route('/rfis')
@login_required
def rfis():
    """List all RFIs for a project"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    rfis = RFI.query.filter_by(project_id=project_id).order_by(RFI.number).all()
    return render_template('projects/engineering/rfis/list.html', 
                          project=project, rfis=rfis)

@engineering_bp.route('/rfis/create', methods=['GET', 'POST'])
@login_required
def create_rfi():
    """Create a new RFI"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = RFIForm()
    
    # Get next RFI number
    last_rfi = RFI.query.filter_by(project_id=project_id).order_by(RFI.id.desc()).first()
    next_number = f"RFI-{(last_rfi.id + 1 if last_rfi else 1):04d}"
    form.number.data = next_number
    
    if form.validate_on_submit():
        rfi = RFI(
            project_id=project_id,
            number=form.number.data,
            subject=form.subject.data,
            question=form.question.data,
            discipline=form.discipline.data,
            status='open',
            date_submitted=datetime.now().date(),
            date_required=form.date_required.data,
            submitted_by=current_user.id
        )
        db.session.add(rfi)
        db.session.commit()
        flash('RFI created successfully!', 'success')
        return redirect(url_for('projects.engineering.rfis', project_id=project_id))
        
    return render_template('projects/engineering/rfis/create.html',
                          project=project, form=form)

@engineering_bp.route('/rfis/<int:id>')
@login_required
def view_rfi(id):
    """View a specific RFI"""
    rfi = RFI.query.get_or_404(id)
    project = Project.query.get_or_404(rfi.project_id)
    
    # Get comments and attachments
    comments = Comment.query.filter_by(record_type='rfi', record_id=id).order_by(Comment.created_at).all()
    attachments = Attachment.query.filter_by(record_type='rfi', record_id=id).all()
    
    return render_template('projects/engineering/rfis/view.html',
                          project=project, rfi=rfi,
                          comments=comments, attachments=attachments)

@engineering_bp.route('/rfis/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rfi(id):
    """Edit an RFI"""
    rfi = RFI.query.get_or_404(id)
    project = Project.query.get_or_404(rfi.project_id)
    form = RFIForm(obj=rfi)
    
    if form.validate_on_submit():
        rfi.number = form.number.data
        rfi.subject = form.subject.data
        rfi.question = form.question.data
        rfi.answer = form.answer.data
        rfi.discipline = form.discipline.data
        rfi.date_required = form.date_required.data
        
        if form.answer.data and not rfi.date_answered and form.answer.data.strip():
            rfi.date_answered = datetime.now().date()
            rfi.answered_by = current_user.id
            rfi.status = 'answered'
        
        db.session.commit()
        flash('RFI updated successfully!', 'success')
        return redirect(url_for('projects.engineering.view_rfi', id=id))
    
    return render_template('projects/engineering/rfis/edit.html',
                          project=project, rfi=rfi, form=form)

@engineering_bp.route('/rfis/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def delete_rfi(id):
    """Delete an RFI"""
    rfi = RFI.query.get_or_404(id)
    project_id = rfi.project_id
    
    # Delete related comments and attachments
    Comment.query.filter_by(record_type='rfi', record_id=id).delete()
    
    # Delete attachment files before deleting records
    attachments = Attachment.query.filter_by(record_type='rfi', record_id=id).all()
    for attachment in attachments:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    
    Attachment.query.filter_by(record_type='rfi', record_id=id).delete()
    
    db.session.delete(rfi)
    db.session.commit()
    
    flash('RFI deleted successfully!', 'success')
    return redirect(url_for('projects.engineering.rfis', project_id=project_id))

@engineering_bp.route('/rfis/<int:id>/comments', methods=['POST'])
@login_required
def add_rfi_comment(id):
    """Add a comment to an RFI"""
    rfi = RFI.query.get_or_404(id)
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('projects.engineering.view_rfi', id=id))
    
    comment = Comment(
        record_type='rfi',
        record_id=id,
        content=content,
        user_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('projects.engineering.view_rfi', id=id))

@engineering_bp.route('/rfis/<int:id>/attachments', methods=['POST'])
@login_required
def add_rfi_attachment(id):
    """Add an attachment to an RFI"""
    rfi = RFI.query.get_or_404(id)
    
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('projects.engineering.view_rfi', id=id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('projects.engineering.view_rfi', id=id))
    
    if file:
        filename = str(uuid.uuid4()) + '_' + file.filename
        upload_dir = os.path.join('app', 'uploads', 'rfis', str(rfi.project_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        attachment = Attachment(
            record_type='rfi',
            record_id=id,
            filename=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_type=file.content_type,
            uploaded_by=current_user.id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        flash('Attachment added successfully!', 'success')
    
    return redirect(url_for('projects.engineering.view_rfi', id=id))

@engineering_bp.route('/rfis/<int:id>/pdf')
@login_required
def rfi_pdf(id):
    """Generate PDF for an RFI"""
    rfi = RFI.query.get_or_404(id)
    project = Project.query.get_or_404(rfi.project_id)
    
    # Get comments for the RFI
    comments = Comment.query.filter_by(record_type='rfi', record_id=id).order_by(Comment.created_at).all()
    
    html = render_template('projects/engineering/rfis/pdf.html',
                          project=project, rfi=rfi,
                          comments=comments)
    
    pdf = generate_pdf(html)
    
    filename = f"RFI_{rfi.number}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        pdf,
        download_name=filename,
        as_attachment=True,
        mimetype='application/pdf'
    )

# Submittal Routes
@engineering_bp.route('/submittals')
@login_required
def submittals():
    """List all submittals for a project"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    submittals = Submittal.query.filter_by(project_id=project_id).order_by(Submittal.number).all()
    return render_template('projects/engineering/submittals/list.html', 
                          project=project, submittals=submittals)

@engineering_bp.route('/submittals/create', methods=['GET', 'POST'])
@login_required
def create_submittal():
    """Create a new submittal"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = SubmittalForm()
    
    # Get next submittal number
    last_submittal = Submittal.query.filter_by(project_id=project_id).order_by(Submittal.id.desc()).first()
    next_number = f"SUBM-{(last_submittal.id + 1 if last_submittal else 1):04d}"
    form.number.data = next_number
    
    if form.validate_on_submit():
        submittal = Submittal(
            project_id=project_id,
            number=form.number.data,
            title=form.title.data,
            description=form.description.data,
            specification_section=form.specification_section.data,
            status='pending',
            date_submitted=datetime.now().date(),
            date_required=form.date_required.data,
            submitted_by=current_user.id
        )
        db.session.add(submittal)
        db.session.commit()
        flash('Submittal created successfully!', 'success')
        return redirect(url_for('projects.engineering.submittals', project_id=project_id))
        
    return render_template('projects/engineering/submittals/create.html',
                          project=project, form=form)

@engineering_bp.route('/submittals/<int:id>')
@login_required
def view_submittal(id):
    """View a specific submittal"""
    submittal = Submittal.query.get_or_404(id)
    project = Project.query.get_or_404(submittal.project_id)
    
    # Get comments and attachments
    comments = Comment.query.filter_by(record_type='submittal', record_id=id).order_by(Comment.created_at).all()
    attachments = Attachment.query.filter_by(record_type='submittal', record_id=id).all()
    
    return render_template('projects/engineering/submittals/view.html',
                          project=project, submittal=submittal,
                          comments=comments, attachments=attachments)

# Implement similar routes for other Engineering modules (Drawings, Specifications, etc.)
# Following the same pattern as RFIs and Submittals