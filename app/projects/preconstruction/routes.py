from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.projects.preconstruction import preconstruction_bp
from .forms import BidderForm, BidPackageForm, BidManualForm
from app.models.preconstruction import QualifiedBidder, BidPackage, BidManual
from app.models.settings import Company
from app.models.base import Comment, Attachment
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from datetime import datetime
import os
from app.models.project import Project
from app.utils.access_control import project_access_required

@preconstruction_bp.route('/<int:project_id>/precontruction')
@project_access_required
@login_required
def index(project_id):
    """Preconstruction dashboard with summary of all modules"""
   
        
    project = Project.query.get_or_404(project_id)
    
    try:
        bidders = QualifiedBidder.query.filter_by(project_id=project_id).count()
    except:
        bidders = 0
        
    try:
        packages = BidPackage.query.filter_by(project_id=project_id).count()
    except:
        packages = 0
        
    try:
        manuals = BidManual.query.filter_by(project_id=project_id).count()
    except:
        manuals = 0
    
    try:
        packages_by_status = db.session.query(
            BidPackage.status, db.func.count(BidPackage.id)
        ).filter_by(project_id=project_id).group_by(BidPackage.status).all()
        
        # Format for chart data
        status_labels = []
        status_data = []
        status_colors = {
            'draft': '#6c757d',
            'issued': '#007bff',
            'under_review': '#ffc107',
            'awarded': '#28a745',
            'closed': '#343a40'
        }
        chart_colors = []
        
        for status, count in packages_by_status:
            status_labels.append(status.replace('_', ' ').title())
            status_data.append(count)
            chart_colors.append(status_colors.get(status, '#6c757d'))
    except:
        status_labels = []
        status_data = []
        chart_colors = []
    
    return render_template('projects/preconstruction/dashboard.html',
                          project=project,
                          bidders=bidders,
                          packages=packages,
                          manuals=manuals,
                          status_labels=status_labels,
                          status_data=status_data,
                          chart_colors=chart_colors)
# Dashboard
@preconstruction_bp.route('/dashboard')
@login_required
def dashboard():
    """Preconstruction dashboard with summary of all modules"""
    project_id = request.args.get('project_id', type=int)
    
    bidders = QualifiedBidder.query.filter_by(project_id=project_id).count()
    packages = BidPackage.query.filter_by(project_id=project_id).count()
    manuals = BidManual.query.filter_by(project_id=project_id).count()
    
    packages_by_status = db.session.query(
        BidPackage.status, db.func.count(BidPackage.id)
    ).filter_by(project_id=project_id).group_by(BidPackage.status).all()
    
    # Format for chart data
    status_labels = []
    status_data = []
    status_colors = {
        'draft': '#6c757d',
        'issued': '#007bff',
        'under_review': '#ffc107',
        'awarded': '#28a745',
        'closed': '#343a40'
    }
    chart_colors = []
    
    for status, count in packages_by_status:
        status_labels.append(status.replace('_', ' ').title())
        status_data.append(count)
        chart_colors.append(status_colors.get(status, '#6c757d'))
    
    return render_template('projects/preconstruction/dashboard.html',
                          project_id=project_id,
                          bidders=bidders,
                          packages=packages,
                          manuals=manuals,
                          status_labels=status_labels,
                          status_data=status_data,
                          chart_colors=chart_colors)

# Qualified Bidders
@preconstruction_bp.route('/<int:project_id>/bidders')
@login_required
def bidders(project_id):
    """List qualified bidders"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    try:
        bidders = QualifiedBidder.query.filter_by(project_id=project_id).all()
    except:
        bidders = []
    
    return render_template('projects/preconstruction/bidders/list.html', 
                          bidders=bidders, project=project)
@preconstruction_bp.route('/<int:project_id>/bidders/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_bidder(project_id):
    """Create a new qualified bidder"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    form = BidderForm()
    
    if form.validate_on_submit():
        try:
            bidder = QualifiedBidder(
                name=form.name.data,
                project_id=project_id,
                company_id=form.company.data.id if form.company.data else None,
                contact_name=form.contact_name.data,
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                qualification_date=form.qualification_date.data,
                qualification_status=form.qualification_status.data,
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(bidder)
            db.session.commit()
            
            flash('Qualified bidder added successfully!', 'success')
            return redirect(url_for('projects_preconstruction.bidders', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bidder: {str(e)}', 'danger')
    
    return render_template('projects/preconstruction/bidders/create.html', 
                          form=form, project=project)
@preconstruction_bp.route('/bidders/<int:id>')
@login_required
def view_bidder(id):
    """View qualified bidder details"""
    bidder = QualifiedBidder.query.get_or_404(id)
    project_id = bidder.project_id
    
    # Get comments related to this bidder
    comments = Comment.query.filter_by(
        record_type='qualified_bidder', record_id=id
    ).order_by(Comment.created_at).all()
    
    # Get attachments related to this bidder
    attachments = Attachment.query.filter_by(
        record_type='qualified_bidder', record_id=id
    ).order_by(Attachment.filename).all()
    
    return render_template('projects/preconstruction/bidders/view.html', 
                          bidder=bidder, project_id=project_id,
                          comments=comments, attachments=attachments)

@preconstruction_bp.route('/bidders/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def edit_bidder(id):
    """Edit qualified bidder"""
    bidder = QualifiedBidder.query.get_or_404(id)
    project_id = bidder.project_id
    
    form = BidderForm(obj=bidder)
    
    if form.validate_on_submit():
        bidder.name = form.name.data
        bidder.company_id = form.company.data.id if form.company.data else None
        bidder.contact_name = form.contact_name.data
        bidder.contact_email = form.contact_email.data
        bidder.contact_phone = form.contact_phone.data
        bidder.qualification_date = form.qualification_date.data
        bidder.qualification_status = form.qualification_status.data
        bidder.notes = form.notes.data
        bidder.updated_by = current_user.id
        bidder.updated_at = datetime.now()
        
        db.session.commit()
        flash('Bidder updated successfully!', 'success')
        return redirect(url_for('projects.preconstruction.view_bidder', id=bidder.id))
    
    return render_template('projects/preconstruction/bidders/edit.html', 
                          form=form, bidder=bidder, project_id=project_id)

@preconstruction_bp.route('/bidders/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin', 'Owner', 'General Contractor'])
def delete_bidder(id):
    """Delete qualified bidder"""
    bidder = QualifiedBidder.query.get_or_404(id)
    project_id = bidder.project_id
    
    db.session.delete(bidder)
    db.session.commit()
    
    flash('Bidder deleted successfully!', 'success')
    return redirect(url_for('projects.preconstruction.bidders', project_id=project_id))

@preconstruction_bp.route('/bidders/<int:id>/pdf')
@login_required
def export_bidder_pdf(id):
    """Export bidder details to PDF"""
    bidder = QualifiedBidder.query.get_or_404(id)
    comments = Comment.query.filter_by(
        record_type='qualified_bidder', record_id=id
    ).order_by(Comment.created_at).all()
    
    html = render_template('projects/preconstruction/bidders/pdf_template.html',
                          bidder=bidder, comments=comments)
    
    # Generate PDF
    pdf = generate_pdf(html)
    filename = f"Qualified_Bidder_{bidder.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Return the PDF as a downloadable file
    return pdf, 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename="{filename}"'
    }

# Comment handling for bidders
@preconstruction_bp.route('/bidders/<int:id>/comments', methods=['POST'])
@login_required
def add_bidder_comment(id):
    """Add a comment to a bidder"""
    bidder = QualifiedBidder.query.get_or_404(id)
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('projects.preconstruction.view_bidder', id=id))
    
    comment = Comment(
        record_type='qualified_bidder',
        record_id=id,
        content=content,
        user_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('projects.preconstruction.view_bidder', id=id))

# File attachment for bidders
@preconstruction_bp.route('/bidders/<int:id>/attachments', methods=['POST'])
@login_required
def add_bidder_attachment(id):
    """Add an attachment to a bidder"""
    bidder = QualifiedBidder.query.get_or_404(id)
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('projects.preconstruction.view_bidder', id=id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('projects.preconstruction.view_bidder', id=id))
    
    # If file is allowed
    if file:
        # Create directory if it doesn't exist
        upload_dir = os.path.join('app', 'uploads', 'bidders', str(id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        filename = file.filename
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Create attachment record
        attachment = Attachment(
            record_type='qualified_bidder',
            record_id=id,
            filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_type=file.content_type,
            uploaded_by=current_user.id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        flash('Attachment uploaded successfully!', 'success')
    
    return redirect(url_for('projects.preconstruction.view_bidder', id=id))


# Bid Packages
@preconstruction_bp.route('/<int:project_id>/packages')
@login_required
def packages(project_id):
    """List bid packages"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    try:
        packages = BidPackage.query.filter_by(project_id=project_id).all()
    except:
        packages = []
    
    return render_template('projects/preconstruction/packages/list.html', 
                          packages=packages, project=project)

@preconstruction_bp.route('/<int:project_id>/packages/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_package(project_id):
    """Create a new bid package"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    form = BidPackageForm()
    
    if form.validate_on_submit():
        try:
            package = BidPackage(
                project_id=project_id,
                name=form.name.data,
                package_number=form.package_number.data,
                description=form.description.data,
                issue_date=form.issue_date.data,
                due_date=form.due_date.data,
                estimated_value=form.estimated_value.data,
                status=form.status.data,
                created_by=current_user.id
            )
            db.session.add(package)
            db.session.commit()
            
            flash('Bid package created successfully!', 'success')
            return redirect(url_for('projects_preconstruction.packages', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bid package: {str(e)}', 'danger')
    
    return render_template('projects/preconstruction/packages/create.html', 
                          form=form, project=project)


# Bid Manuals
@preconstruction_bp.route('/<int:project_id>/manuals')
@login_required
def manuals(project_id):
    """List bid manuals"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    
    try:
        manuals = BidManual.query.filter_by(project_id=project_id).all()
    except:
        manuals = []
    
    return render_template('projects/preconstruction/manuals/list.html', 
                          manuals=manuals, project=project)


@preconstruction_bp.route('/<int:project_id>/manuals/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_manual(project_id):
    """Create a new bid manual"""
    # Check if user has access
    if not has_project_access(current_user, project_id):
        flash("You don't have access to this project.", "danger")
        return redirect(url_for('projects.index'))
        
    project = Project.query.get_or_404(project_id)
    form = BidManualForm()
    
    if form.validate_on_submit():
        try:
            manual = BidManual(
                project_id=project_id,
                title=form.title.data,
                version=form.version.data,
                description=form.description.data,
                issue_date=form.issue_date.data,
                created_by=current_user.id
            )
            db.session.add(manual)
            db.session.commit()
            
            flash('Bid manual created successfully!', 'success')
            return redirect(url_for('projects_preconstruction.manuals', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bid manual: {str(e)}', 'danger')
    
    return render_template('projects/preconstruction/manuals/create.html', 
                          form=form, project=project)