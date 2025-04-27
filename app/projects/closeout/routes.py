from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.closeout import (
    OperationAndMaintenanceManual, Warranty, AtticStock, 
    FinalInspection, AsBuiltDrawing, CloseoutDocument
)
from app.projects.closeout.forms import (
    OMManualForm, WarrantyForm, AtticStockForm, 
    FinalInspectionForm, AsBuiltDrawingForm, CloseoutDocumentForm
)
from app.extensions import db
from app.utils.access_control import project_access_required
from app.utils.file_upload import save_file, get_file_url, delete_file
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os
import uuid

closeout_bp = Blueprint('projects_closeout', __name__)

@closeout_bp.route('/<int:project_id>/clouseout')
@project_access_required
@login_required
def index(project_id):
    """Closeout dashboard view"""
    # Check if user has access
    
        
    project = Project.query.get_or_404(project_id)
    
    # Get counts for widgets
    try:
        manual_count = OperationAndMaintenanceManual.query.filter_by(project_id=project_id).count()
    except:
        manual_count = 0
        
    try:
        warranty_count = Warranty.query.filter_by(project_id=project_id).count()
    except:
        warranty_count = 0
        
    try:
        attic_stock_count = AtticStock.query.filter_by(project_id=project_id).count()
    except:
        attic_stock_count = 0
        
    try:
        inspection_count = FinalInspection.query.filter_by(project_id=project_id).count()
    except:
        inspection_count = 0
        
    try:
        asbuilt_count = AsBuiltDrawing.query.filter_by(project_id=project_id).count()
    except:
        asbuilt_count = 0
        
    try:
        document_count = CloseoutDocument.query.filter_by(project_id=project_id).count()
    except:
        document_count = 0
    
    # Get expiring warranties (next 30 days)
    try:
        today = datetime.today().date()
        expiring_soon = Warranty.query.filter(
            Warranty.project_id == project_id,
            Warranty.end_date >= today,
            Warranty.end_date <= today + timedelta(days=30),
            Warranty.status == 'active'
        ).order_by(Warranty.end_date.asc()).all()
    except:
        expiring_soon = []
    
    # Get recent documents
    try:
        recent_documents = CloseoutDocument.query.filter_by(
            project_id=project_id
        ).order_by(CloseoutDocument.created_at.desc()).limit(5).all()
    except:
        recent_documents = []
    
    return render_template('projects/closeout/dashboard.html',
                           project=project,
                           manual_count=manual_count,
                           warranty_count=warranty_count,
                           attic_stock_count=attic_stock_count,
                           inspection_count=inspection_count,
                           asbuilt_count=asbuilt_count,
                           document_count=document_count,
                           expiring_soon=expiring_soon,
                           recent_documents=recent_documents)
# Dashboard view
@closeout_bp.route('/dashboard')
@login_required
@project_access_required
def dashboard():
    """Closeout dashboard view"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get counts for widgets
    manual_count = OperationAndMaintenanceManual.query.filter_by(project_id=project_id).count()
    warranty_count = Warranty.query.filter_by(project_id=project_id).count()
    attic_stock_count = AtticStock.query.filter_by(project_id=project_id).count()
    inspection_count = FinalInspection.query.filter_by(project_id=project_id).count()
    asbuilt_count = AsBuiltDrawing.query.filter_by(project_id=project_id).count()
    document_count = CloseoutDocument.query.filter_by(project_id=project_id).count()
    
    # Get expiring warranties (next 30 days)
    today = datetime.today().date()
    expiring_soon = Warranty.query.filter(
        Warranty.project_id == project_id,
        Warranty.end_date >= today,
        Warranty.end_date <= today + timedelta(days=30),
        Warranty.status == 'active'
    ).order_by(Warranty.end_date.asc()).all()
    
    # Get recent documents
    recent_documents = CloseoutDocument.query.filter_by(
        project_id=project_id
    ).order_by(CloseoutDocument.created_at.desc()).limit(5).all()
    
    return render_template('projects/closeout/dashboard.html',
                           project=project,
                           manual_count=manual_count,
                           warranty_count=warranty_count,
                           attic_stock_count=attic_stock_count,
                           inspection_count=inspection_count,
                           asbuilt_count=asbuilt_count,
                           document_count=document_count,
                           expiring_soon=expiring_soon,
                           recent_documents=recent_documents)
@closeout_bp.route('/<int:project_id>/manuals')
@login_required
def manuals(project_id):
    """List all operation and maintenance manuals"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    try:
        query = OperationAndMaintenanceManual.query.filter_by(project_id=project_id)
        
        if category != 'all':
            query = query.filter_by(equipment_category=category)
        
        if search:
            query = query.filter(
                db.or_(
                    OperationAndMaintenanceManual.title.ilike(f'%{search}%'),
                    OperationAndMaintenanceManual.description.ilike(f'%{search}%'),
                    OperationAndMaintenanceManual.manufacturer.ilike(f'%{search}%'),
                    OperationAndMaintenanceManual.model_number.ilike(f'%{search}%'),
                    OperationAndMaintenanceManual.location.ilike(f'%{search}%')
                )
            )
        
        manuals = query.order_by(OperationAndMaintenanceManual.title).all()
        
        # Get unique categories for filter
        categories = db.session.query(OperationAndMaintenanceManual.equipment_category).filter(
            OperationAndMaintenanceManual.project_id == project_id,
            OperationAndMaintenanceManual.equipment_category != None,
            OperationAndMaintenanceManual.equipment_category != ''
        ).distinct().all()
    except:
        manuals = []
        categories = []
    
    return render_template('projects/closeout/manuals.html',
                           project=project,
                           manuals=manuals,
                           categories=[cat[0] for cat in categories if cat[0]],
                           selected_category=category,
                           search=search)

@closeout_bp.route('/manuals/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_manual():
    """Create a new O&M manual"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    form = OMManualForm()
    
    if form.validate_on_submit():
        manual = OperationAndMaintenanceManual()
        manual.project_id = project_id
        manual.title = form.title.data
        manual.description = form.description.data
        manual.equipment_category = form.equipment_category.data
        manual.manufacturer = form.manufacturer.data
        manual.model_number = form.model_number.data
        manual.location = form.location.data
        manual.submission_date = form.submission_date.data
        manual.notes = form.notes.data
        manual.created_by = current_user.id
        
        # Handle file upload
        if form.manual_file.data:
            filename = save_file(
                form.manual_file.data, 
                f'projects/{project_id}/closeout/manuals',
                name_prefix=f'manual_{uuid.uuid4().hex}'
            )
            
            if filename:
                manual.file_path = filename
                manual.file_name = form.manual_file.data.filename
                manual.file_size = len(form.manual_file.data.read())
                form.manual_file.data.seek(0)  # Reset file pointer after reading
        
        db.session.add(manual)
        db.session.commit()
        
        flash('Operation and maintenance manual has been added.', 'success')
        return redirect(url_for('projects.closeout.manuals', project_id=project_id))
    
    return render_template('projects/closeout/create_manual.html',
                           project=project,
                           form=form)

@closeout_bp.route('/manuals/<int:manual_id>')
@login_required
@project_access_required
def view_manual(manual_id):
    """View manual details"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    manual = OperationAndMaintenanceManual.query.get_or_404(manual_id)
    
    if manual.project_id != project_id:
        flash('Manual not found in this project.', 'danger')
        return redirect(url_for('projects.closeout.manuals', project_id=project_id))
    
    return render_template('projects/closeout/view_manual.html',
                           project=project,
                           manual=manual)

@closeout_bp.route('/manuals/<int:manual_id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_manual(manual_id):
    """Edit an O&M manual"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    manual = OperationAndMaintenanceManual.query.get_or_404(manual_id)
    
    if manual.project_id != project_id:
        flash('Manual not found in this project.', 'danger')
        return redirect(url_for('projects.closeout.manuals', project_id=project_id))
    
    form = OMManualForm(obj=manual)
    
    if form.validate_on_submit():
        manual.title = form.title.data
        manual.description = form.description.data
        manual.equipment_category = form.equipment_category.data
        manual.manufacturer = form.manufacturer.data
        manual.model_number = form.model_number.data
        manual.location = form.location.data
        manual.submission_date = form.submission_date.data
        manual.notes = form.notes.data
        
        # Handle file upload
        if form.manual_file.data:
            # Delete the old file if it exists
            if manual.file_path:
                delete_file(manual.file_path)
            
            filename = save_file(
                form.manual_file.data, 
                f'projects/{project_id}/closeout/manuals',
                name_prefix=f'manual_{uuid.uuid4().hex}'
            )
            
            if filename:
                manual.file_path = filename
                manual.file_name = form.manual_file.data.filename
                manual.file_size = len(form.manual_file.data.read())
                form.manual_file.data.seek(0)
        
        db.session.commit()
        
        flash('Manual has been updated.', 'success')
        return redirect(url_for('projects.closeout.view_manual', project_id=project_id, manual_id=manual_id))
    
    return render_template('projects/closeout/edit_manual.html',
                           project=project,
                           manual=manual,
                           form=form)

@closeout_bp.route('/manuals/<int:manual_id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_manual(manual_id):
    """Delete an O&M manual"""
    project_id = request.args.get('project_id', type=int)
    
    manual = OperationAndMaintenanceManual.query.get_or_404(manual_id)
    
    if manual.project_id != project_id:
        flash('Manual not found in this project.', 'danger')
        return redirect(url_for('projects.closeout.manuals', project_id=project_id))
    
    # Delete associated file
    if manual.file_path:
        delete_file(manual.file_path)
    
    db.session.delete(manual)
    db.session.commit()
    
    flash('Manual has been deleted.', 'success')
    return redirect(url_for('projects.closeout.manuals', project_id=project_id))

@closeout_bp.route('/manuals/<int:manual_id>/download')
@login_required
@project_access_required
def download_manual(manual_id):
    """Download manual file"""
    project_id = request.args.get('project_id', type=int)
    manual = OperationAndMaintenanceManual.query.get_or_404(manual_id)
    
    if manual.project_id != project_id or not manual.file_path:
        flash('File not found.', 'danger')
        return redirect(url_for('projects.closeout.view_manual', project_id=project_id, manual_id=manual_id))
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    directory = os.path.dirname(os.path.join(upload_folder, manual.file_path))
    filename = os.path.basename(manual.file_path)
    
    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True,
        download_name=manual.file_name or filename
    )

# Similar routes for Warranties, Attic Stock, Final Inspections, As-Built Drawings, and Closeout Documents
# I'll implement warranties as an example, and the others would follow the same pattern
@closeout_bp.route('/<int:project_id>/warranties')
@login_required
def warranties(project_id):
    """List all warranties"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    try:
        query = Warranty.query.filter_by(project_id=project_id)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                db.or_(
                    Warranty.title.ilike(f'%{search}%'),
                    Warranty.description.ilike(f'%{search}%'),
                    Warranty.manufacturer.ilike(f'%{search}%'),
                    Warranty.supplier.ilike(f'%{search}%'),
                    Warranty.contractor.ilike(f'%{search}%'),
                    Warranty.equipment_category.ilike(f'%{search}%')
                )
            )
        
        warranties = query.order_by(Warranty.end_date).all()
    except:
        warranties = []
    
    return render_template('projects/closeout/warranties.html',
                           project=project,
                           warranties=warranties,
                           selected_status=status,
                           search=search)

@closeout_bp.route('/warranties/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_warranty():
    """Create a new warranty"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    form = WarrantyForm()
    
    if form.validate_on_submit():
        warranty = Warranty()
        warranty.project_id = project_id
        warranty.title = form.title.data
        warranty.description = form.description.data
        warranty.warranty_type = form.warranty_type.data
        warranty.status = form.status.data
        
        warranty.manufacturer = form.manufacturer.data
        warranty.supplier = form.supplier.data
        warranty.contractor = form.contractor.data
        warranty.contact_name = form.contact_name.data
        warranty.contact_phone = form.contact_phone.data
        warranty.contact_email = form.contact_email.data
        
        warranty.equipment_category = form.equipment_category.data
        warranty.model_number = form.model_number.data
        warranty.serial_number = form.serial_number.data
        warranty.location = form.location.data
        
        warranty.start_date = form.start_date.data
        warranty.end_date = form.end_date.data
        warranty.duration_months = form.duration_months.data
        
        warranty.terms_conditions = form.terms_conditions.data
        warranty.exclusions = form.exclusions.data
        warranty.maintenance_requirements = form.maintenance_requirements.data
        
        warranty.created_by = current_user.id
        
        # Handle file upload
        if form.warranty_file.data:
            filename = save_file(
                form.warranty_file.data, 
                f'projects/{project_id}/closeout/warranties',
                name_prefix=f'warranty_{uuid.uuid4().hex}'
            )
            
            if filename:
                warranty.file_path = filename
                warranty.file_name = form.warranty_file.data.filename
                warranty.file_size = len(form.warranty_file.data.read())
                form.warranty_file.data.seek(0)
        
        db.session.add(warranty)
        db.session.commit()
        
        flash('Warranty has been added.', 'success')
        return redirect(url_for('projects.closeout.warranties', project_id=project_id))
    
    return render_template('projects/closeout/create_warranty.html',
                           project=project,
                           form=form)

# Attic Stock routes
@closeout_bp.route('/<int:project_id>/attic-stock')
@login_required
def attic_stock(project_id):
    """List all attic stock items"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    try:
        attic_stock_items = AtticStock.query.filter_by(project_id=project_id).order_by(
            AtticStock.material_name).all()
    except:
        attic_stock_items = []
    
    return render_template('projects/closeout/attic_stock.html',
                           project=project,
                           attic_stock_items=attic_stock_items)

# Final Inspections routes
@closeout_bp.route('/<int:project_id>/inspections')
@login_required
def inspections(project_id):
    """List all final inspections"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    try:
        inspections = FinalInspection.query.filter_by(project_id=project_id).order_by(
            FinalInspection.inspection_date.desc()).all()
    except:
        inspections = []
    
    return render_template('projects/closeout/inspections.html',
                           project=project,
                           inspections=inspections)



# As-Built Drawings routes
@closeout_bp.route('/<int:project_id>/as-builts')
@login_required
def as_builts(project_id):
    """List all as-built drawings"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    discipline = request.args.get('discipline', 'all')
    
    try:
        query = AsBuiltDrawing.query.filter_by(project_id=project_id)
        
        if discipline != 'all':
            query = query.filter_by(discipline=discipline)
        
        drawings = query.order_by(AsBuiltDrawing.title).all()
    except:
        drawings = []
    
    return render_template('projects/closeout/as_builts.html',
                           project=project,
                           drawings=drawings,
                           selected_discipline=discipline)


# Closeout Documents routes
@closeout_bp.route('/<int:project_id>/documents')
@login_required
def documents(project_id):
    """List all closeout documents"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    document_type = request.args.get('type', 'all')
    
    try:
        query = CloseoutDocument.query.filter_by(project_id=project_id)
        
        if document_type != 'all':
            query = query.filter_by(document_type=document_type)
        
        documents = query.order_by(CloseoutDocument.title).all()
    except:
        documents = []
    
    return render_template('projects/closeout/documents.html',
                           project=project,
                           documents=documents,
                           selected_type=document_type)
# Add similar view, edit, and delete routes for warranties as we did for manuals