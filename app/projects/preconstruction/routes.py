from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from . import preconstruction_bp
from .forms import BidderForm, BidPackageForm, BidManualForm
from .models import QualifiedBidder, BidPackage, BidManual
from app.models.settings import Company
from app.models.base import Comment, Attachment
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from datetime import datetime
import os

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
@preconstruction_bp.route('/bidders')
@login_required
def bidders():
    """List qualified bidders"""
    project_id = request.args.get('project_id', type=int)
    bidders = QualifiedBidder.query.filter_by(project_id=project_id).all()
    return render_template('projects/preconstruction/bidders/list.html', 
                          bidders=bidders, project_id=project_id)

@preconstruction_bp.route('/bidders/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_bidder():
    """Create a new qualified bidder"""
    project_id = request.args.get('project_id', type=int)
    form = BidderForm()
    
    if form.validate_on_submit():
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
        return redirect(url_for('projects.preconstruction.bidders', project_id=project_id))
    
    return render_template('projects/preconstruction/bidders/create.html', 
                          form=form, project_id=project_id)

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