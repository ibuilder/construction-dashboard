from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import cost_bp
from .forms import BudgetForm, BudgetItemForm, InvoiceForm, ChangeOrderForm, PotentialChangeOrderForm
from app.models.cost import Budget, BudgetItem, Invoice, ChangeOrder, PotentialChangeOrder, DirectCost, ApprovalLetter
from app.models.base import Comment, Attachment
from app.models.project import Project
from app.extensions import db
from app.utils.access_control import role_required
from app.utils.pdf_generator import generate_pdf
from app.utils.web3_utils import store_hash_on_blockchain, verify_document_hash
from datetime import datetime
import hashlib
import os
import uuid

# Cost Dashboard
@cost_bp.route('/dashboard')
@login_required
def dashboard():
    """Cost dashboard with summary of all modules"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to view cost data
    if current_user.role not in ['Admin', 'Owner', 'Owners Representative', 'General Contractor']:
        flash('You do not have permission to view cost information', 'danger')
        return redirect(url_for('projects.view_project', id=project_id))
    
    # Get budget summary
    budget = Budget.query.filter_by(project_id=project_id).first()
    budget_items = BudgetItem.query.filter_by(project_id=project_id).all() if budget else []
    
    original_budget = sum(item.original_amount for item in budget_items)
    current_budget = sum(item.current_amount for item in budget_items)
    committed_cost = sum(item.committed_cost for item in budget_items)
    projected_cost = sum(item.projected_cost for item in budget_items)
    
    # Calculate variance
    variance = current_budget - projected_cost
    variance_percent = (variance / current_budget * 100) if current_budget > 0 else 0
    
    # Get change orders summary
    approved_changes = db.session.query(db.func.sum(ChangeOrder.amount)).filter(
        ChangeOrder.project_id == project_id,
        ChangeOrder.status == 'approved'
    ).scalar() or 0
    
    pending_changes = db.session.query(db.func.sum(PotentialChangeOrder.estimated_amount)).filter(
        PotentialChangeOrder.project_id == project_id,
        PotentialChangeOrder.status == 'pending'
    ).scalar() or 0
    
    # Get invoices summary
    total_invoiced = db.session.query(db.func.sum(Invoice.amount)).filter(
        Invoice.project_id == project_id
    ).scalar() or 0
    
    paid_invoiced = db.session.query(db.func.sum(Invoice.amount)).filter(
        Invoice.project_id == project_id,
        Invoice.status == 'paid'
    ).scalar() or 0
    
    # Get direct costs
    direct_costs = db.session.query(db.func.sum(DirectCost.amount)).filter(
        DirectCost.project_id == project_id
    ).scalar() or 0
    
    # Get cost data by category for chart
    budget_by_category = db.session.query(
        BudgetItem.category, db.func.sum(BudgetItem.original_amount).label('original'),
        db.func.sum(BudgetItem.current_amount).label('current'),
        db.func.sum(BudgetItem.committed_cost).label('committed'),
        db.func.sum(BudgetItem.projected_cost).label('projected')
    ).filter(
        BudgetItem.project_id == project_id
    ).group_by(BudgetItem.category).all()
    
    # Format for charts
    categories = []
    original_data = []
    current_data = []
    committed_data = []
    projected_data = []
    
    for category, original, current, committed, projected in budget_by_category:
        categories.append(category)
        original_data.append(float(original))
        current_data.append(float(current))
        committed_data.append(float(committed))
        projected_data.append(float(projected))
    
    return render_template('projects/cost/dashboard.html',
                          project=project,
                          original_budget=original_budget,
                          current_budget=current_budget,
                          committed_cost=committed_cost,
                          projected_cost=projected_cost,
                          variance=variance,
                          variance_percent=variance_percent,
                          approved_changes=approved_changes,
                          pending_changes=pending_changes,
                          total_invoiced=total_invoiced,
                          paid_invoiced=paid_invoiced,
                          direct_costs=direct_costs,
                          categories=categories,
                          original_data=original_data,
                          current_data=current_data,
                          committed_data=committed_data,
                          projected_data=projected_data)

# Budget Routes
@cost_bp.route('/budget')
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def budget():
    """View project budget"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Get main budget
    budget = Budget.query.filter_by(project_id=project_id).first()
    
    # Get budget items
    budget_items = BudgetItem.query.filter_by(project_id=project_id).order_by(BudgetItem.code).all()
    
    # Calculate totals
    total_original = sum(item.original_amount for item in budget_items)
    total_current = sum(item.current_amount for item in budget_items)
    total_committed = sum(item.committed_cost for item in budget_items)
    total_projected = sum(item.projected_cost for item in budget_items)
    
    # Calculate variance
    total_variance = total_current - total_projected
    
    return render_template('projects/cost/budget/view.html',
                          project=project,
                          budget=budget,
                          budget_items=budget_items,
                          total_original=total_original,
                          total_current=total_current,
                          total_committed=total_committed,
                          total_projected=total_projected,
                          total_variance=total_variance)

@cost_bp.route('/budget/setup', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative'])
def setup_budget():
    """Create or update main budget"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Check if budget already exists
    budget = Budget.query.filter_by(project_id=project_id).first()
    
    if budget:
        form = BudgetForm(obj=budget)
    else:
        form = BudgetForm()
        form.version.data = '1.0'
    
    if form.validate_on_submit():
        if budget:
            # Update existing budget
            form.populate_obj(budget)
            budget.updated_by = current_user.id
            budget.updated_at = datetime.now()
            flash('Budget updated successfully!', 'success')
        else:
            # Create new budget
            budget = Budget(
                project_id=project_id,
                version=form.version.data,
                description=form.description.data,
                notes=form.notes.data,
                created_by=current_user.id
            )
            db.session.add(budget)
            flash('Budget created successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('projects.cost.budget', project_id=project_id))
    
    return render_template('projects/cost/budget/setup.html',
                          project=project, form=form, budget=budget)

@cost_bp.route('/budget/items/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative'])
def add_budget_item():
    """Add a budget item"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = BudgetItemForm()
    
    if form.validate_on_submit():
        budget_item = BudgetItem(
            project_id=project_id,
            code=form.code.data,
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            original_amount=form.original_amount.data,
            current_amount=form.original_amount.data,  # Initially same as original
            committed_cost=form.committed_cost.data or 0,
            projected_cost=form.projected_cost.data or 0,
            created_by=current_user.id
        )
        db.session.add(budget_item)
        db.session.commit()
        
        flash('Budget item added successfully!', 'success')
        return redirect(url_for('projects.cost.budget', project_id=project_id))
    
    return render_template('projects/cost/budget/add_item.html',
                          project=project, form=form)

# Change Order Routes
@cost_bp.route('/change-orders')
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def change_orders():
    """List all change orders"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    change_orders = ChangeOrder.query.filter_by(project_id=project_id).order_by(
        ChangeOrder.number).all()
    
    # Calculate totals
    approved_total = sum(co.amount for co in change_orders if co.status == 'approved')
    pending_total = sum(co.amount for co in change_orders if co.status == 'pending')
    rejected_total = sum(co.amount for co in change_orders if co.status == 'rejected')
    
    return render_template('projects/cost/change_orders/list.html',
                          project=project,
                          change_orders=change_orders,
                          approved_total=approved_total,
                          pending_total=pending_total,
                          rejected_total=rejected_total)

@cost_bp.route('/change-orders/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_change_order():
    """Create a new change order"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = ChangeOrderForm()
    
    # Get next change order number
    last_co = ChangeOrder.query.filter_by(project_id=project_id).order_by(
        ChangeOrder.id.desc()).first()
    next_number = f"CO-{(last_co.id + 1 if last_co else 1):04d}"
    form.number.data = next_number
    
    if form.validate_on_submit():
        change_order = ChangeOrder(
            project_id=project_id,
            number=form.number.data,
            title=form.title.data,
            description=form.description.data,
            reason=form.reason.data,
            amount=form.amount.data,
            status='pending',
            date_issued=form.date_issued.data or datetime.now().date(),
            date_required=form.date_required.data,
            budget_item_id=form.budget_item_id.data if form.budget_item_id.data else None,
            created_by=current_user.id
        )
        db.session.add(change_order)
        db.session.commit()
        
        # If there's a related PCO, update its status
        if form.pco_id.data:
            pco = PotentialChangeOrder.query.get(form.pco_id.data)
            if pco:
                pco.status = 'converted'
                pco.change_order_id = change_order.id
                db.session.commit()
        
        flash('Change order created successfully!', 'success')
        return redirect(url_for('projects.cost.change_orders', project_id=project_id))
    
    return render_template('projects/cost/change_orders/create.html',
                          project=project, form=form)

# Invoice Routes
@cost_bp.route('/invoices')
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def invoices():
    """List all invoices"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    invoices = Invoice.query.filter_by(project_id=project_id).order_by(
        Invoice.invoice_date.desc()).all()
    
    # Calculate totals
    total_amount = sum(inv.amount for inv in invoices)
    paid_amount = sum(inv.amount for inv in invoices if inv.status == 'paid')
    pending_amount = sum(inv.amount for inv in invoices if inv.status == 'pending')
    
    return render_template('projects/cost/invoices/list.html',
                          project=project,
                          invoices=invoices,
                          total_amount=total_amount,
                          paid_amount=paid_amount,
                          pending_amount=pending_amount)

@cost_bp.route('/invoices/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Owner', 'Owners Representative', 'General Contractor'])
def create_invoice():
    """Create a new invoice"""
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = InvoiceForm()
    
    if form.validate_on_submit():
        invoice = Invoice(
            project_id=project_id,
            invoice_number=form.invoice_number.data,
            vendor_id=form.vendor.data.id if form.vendor.data else None,
            description=form.description.data,
            amount=form.amount.data,
            tax_amount=form.tax_amount.data or 0,
            status='pending',
            invoice_date=form.invoice_date.data or datetime.now().date(),
            due_date=form.due_date.data,
            created_by=current_user.id
        )
        db.session.add(invoice)
        db.session.commit()
        
        flash('Invoice created successfully!', 'success')
        
        # If file was uploaded, save it as an attachment
        if 'invoice_file' in request.files and request.files['invoice_file'].filename:
            file = request.files['invoice_file']
            
            # Create directory if it doesn't exist
            upload_dir = os.path.join('app', 'uploads', 'invoices', str(project_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = str(uuid.uuid4()) + '_' + file.filename
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Create attachment record
            attachment = Attachment(
                record_type='invoice',
                record_id=invoice.id,
                filename=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type,
                uploaded_by=current_user.id
            )
            
            # Calculate file hash for blockchain verification
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Store hash on blockchain if enabled
            if project.blockchain_enabled:
                success, result = store_hash_on_blockchain(
                    'invoice', 
                    invoice.id, 
                    file_hash, 
                    f"Invoice {invoice.invoice_number} for {invoice.amount}"
                )
                
                if success:
                    attachment.blockchain_tx = result.get('tx_hash')
                    attachment.blockchain_verified = True
                    flash('Invoice document hash stored on blockchain for verification', 'info')
            
            db.session.add(attachment)
            db.session.commit()
        
        return redirect(url_for('projects.cost.invoices', project_id=project_id))
    
    return render_template('projects/cost/invoices/create.html',
                          project=project, form=form)