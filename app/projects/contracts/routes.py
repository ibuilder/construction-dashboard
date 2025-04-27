from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.contracts import (
    PrimeContract, Subcontract, ProfessionalServiceAgreement,
    LienWaiver, CertificateOfInsurance, LetterOfIntent,
    ContractChangeOrder, ContractDocument, ContractStatus
)
from app.projects.contracts.forms import (
    PrimeContractForm, SubcontractForm, AgreementForm,
    LienWaiverForm, InsuranceForm, LetterOfIntentForm,
    ChangeOrderForm
)
from app.extensions import db
from app.utils.access_control import project_access_required
from app.utils.file_upload import save_file, get_file_url, delete_file
from datetime import datetime, date
import os
import uuid

contracts_bp = Blueprint('projects_contracts', __name__)

# Prime Contracts
@contracts_bp.route('/contracts')
@login_required
@project_access_required
def index():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    
    # Count summary for dashboard
    prime_count = PrimeContract.query.filter_by(project_id=project_id).count()
    subcontract_count = Subcontract.query.filter_by(project_id=project_id).count() 
    agreement_count = ProfessionalServiceAgreement.query.filter_by(project_id=project_id).count()
    loi_count = LetterOfIntent.query.filter_by(project_id=project_id).count()
    insurance_count = CertificateOfInsurance.query.filter_by(project_id=project_id).count()
    lien_waiver_count = LienWaiver.query.filter_by(project_id=project_id).count()
    
    # Get expired or expiring soon insurance
    today = date.today()
    expiring_insurance = CertificateOfInsurance.query.filter(
        CertificateOfInsurance.project_id == project_id,
        CertificateOfInsurance.expiration_date <= today.replace(day=today.day + 30)
    ).order_by(CertificateOfInsurance.expiration_date).limit(5).all()
    
    # Get recent contracts
    recent_contracts = PrimeContract.query.filter_by(project_id=project_id).order_by(
        PrimeContract.created_at.desc()
    ).limit(5).all()
    
    # Get recent subcontracts
    recent_subcontracts = Subcontract.query.filter_by(project_id=project_id).order_by(
        Subcontract.created_at.desc()
    ).limit(5).all()
    
    return render_template('projects/contracts/dashboard.html', 
                           project=project,
                           prime_count=prime_count,
                           subcontract_count=subcontract_count,
                           agreement_count=agreement_count,
                           loi_count=loi_count,
                           insurance_count=insurance_count,
                           lien_waiver_count=lien_waiver_count,
                           expiring_insurance=expiring_insurance,
                           recent_contracts=recent_contracts,
                           recent_subcontracts=recent_subcontracts)

@contracts_bp.route('/contracts')
@login_required
@project_access_required
def contracts():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    contracts = PrimeContract.query.filter_by(project_id=project_id).order_by(PrimeContract.created_at.desc()).all()
    return render_template('projects/contracts/prime/list.html', project=project, contracts=contracts)

@contracts_bp.route('/contracts/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_contract():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = PrimeContractForm()
    
    if form.validate_on_submit():
        contract = PrimeContract(
            project_id=project_id,
            contract_number=form.contract_number.data or f"PC-{project_id}-{uuid.uuid4().hex[:6].upper()}",
            title=form.title.data,
            description=form.description.data,
            contract_type=form.contract_type.data,
            contract_value=form.contract_value.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            client_name=form.client_name.data,
            client_contact=form.client_contact.data,
            client_email=form.client_email.data,
            client_phone=form.client_phone.data,
            retainage_percent=form.retainage_percent.data,
            payment_terms=form.payment_terms.data,
            executed_date=form.executed_date.data,
            signed_by=form.signed_by.data,
            status=ContractStatus.ACTIVE if form.executed_date.data else ContractStatus.PENDING,
            revised_value=form.contract_value.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.contract_document.data:
            file_path = save_file(
                form.contract_document.data,
                f'contracts/prime/{contract.contract_number}',
                f'contract_{uuid.uuid4().hex}'
            )
            if file_path:
                contract.document_path = file_path
        
        db.session.add(contract)
        db.session.commit()
        flash('Contract created successfully!', 'success')
        return redirect(url_for('projects.contracts.contracts', project_id=project_id))
    
    return render_template('projects/contracts/prime/create.html', project=project, form=form)

@contracts_bp.route('/contracts/<int:id>')
@login_required
@project_access_required
def view_contract(id):
    contract = PrimeContract.query.get_or_404(id)
    project = Project.query.get_or_404(contract.project_id)
    
    # Get related change orders
    change_orders = ContractChangeOrder.query.filter_by(
        contract_id=id, contract_type='prime'
    ).order_by(ContractChangeOrder.created_at.desc()).all()
    
    # Get related documents
    documents = ContractDocument.query.filter_by(
        contract_id=id, contract_type='prime'
    ).order_by(ContractDocument.uploaded_at.desc()).all()
    
    return render_template('projects/contracts/prime/view.html', 
                           project=project, 
                           contract=contract,
                           change_orders=change_orders,
                           documents=documents)

@contracts_bp.route('/contracts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@project_access_required
def edit_contract(id):
    contract = PrimeContract.query.get_or_404(id)
    project = Project.query.get_or_404(contract.project_id)
    form = PrimeContractForm(obj=contract)
    
    if form.validate_on_submit():
        form.populate_obj(contract)
        
        # Update status based on executed date
        if form.executed_date.data and contract.status == ContractStatus.PENDING:
            contract.status = ContractStatus.ACTIVE
        
        # Handle document upload
        if form.contract_document.data:
            file_path = save_file(
                form.contract_document.data,
                f'contracts/prime/{contract.contract_number}',
                f'contract_{uuid.uuid4().hex}'
            )
            if file_path:
                # Delete old document if exists
                if contract.document_path:
                    delete_file(contract.document_path)
                contract.document_path = file_path
        
        db.session.commit()
        flash('Contract updated successfully!', 'success')
        return redirect(url_for('projects.contracts.view_contract', id=contract.id, project_id=project.id))
    
    return render_template('projects/contracts/prime/edit.html', project=project, contract=contract, form=form)

@contracts_bp.route('/contracts/<int:id>/delete', methods=['POST'])
@login_required
@project_access_required
def delete_contract(id):
    contract = PrimeContract.query.get_or_404(id)
    project_id = contract.project_id
    
    # Delete associated change orders
    change_orders = ContractChangeOrder.query.filter_by(contract_id=id, contract_type='prime').all()
    for co in change_orders:
        db.session.delete(co)
    
    # Delete associated documents
    documents = ContractDocument.query.filter_by(contract_id=id, contract_type='prime').all()
    for doc in documents:
        if doc.file_path:
            delete_file(doc.file_path)
        db.session.delete(doc)
    
    # Delete contract document
    if contract.document_path:
        delete_file(contract.document_path)
    
    db.session.delete(contract)
    db.session.commit()
    
    flash('Contract deleted successfully!', 'success')
    return redirect(url_for('projects.contracts.contracts', project_id=project_id))

# Subcontracts
@contracts_bp.route('/subcontracts')
@login_required
@project_access_required
def subcontracts():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    subcontracts = Subcontract.query.filter_by(project_id=project_id).order_by(Subcontract.created_at.desc()).all()
    return render_template('projects/contracts/subcontracts/list.html', project=project, subcontracts=subcontracts)

@contracts_bp.route('/subcontracts/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_subcontract():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = SubcontractForm()
    
    if form.validate_on_submit():
        subcontract = Subcontract(
            project_id=project_id,
            subcontract_number=form.subcontract_number.data or f"SC-{project_id}-{uuid.uuid4().hex[:6].upper()}",
            title=form.title.data,
            description=form.description.data,
            subcontract_type=form.subcontract_type.data,
            subcontract_value=form.subcontract_value.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            company_name=form.company_name.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            scope_of_work=form.scope_of_work.data,
            retainage_percent=form.retainage_percent.data,
            payment_terms=form.payment_terms.data,
            executed_date=form.executed_date.data,
            signed_by=form.signed_by.data,
            insurance_expiration=form.insurance_expiration.data,
            bonded=form.bonded.data,
            bond_company=form.bond_company.data,
            status=ContractStatus.ACTIVE if form.executed_date.data else ContractStatus.PENDING,
            revised_value=form.subcontract_value.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.contract_document.data:
            file_path = save_file(
                form.contract_document.data,
                f'contracts/subcontracts/{subcontract.subcontract_number}',
                f'subcontract_{uuid.uuid4().hex}'
            )
            if file_path:
                subcontract.document_path = file_path
        
        db.session.add(subcontract)
        db.session.commit()
        flash('Subcontract created successfully!', 'success')
        return redirect(url_for('projects.contracts.subcontracts', project_id=project_id))
    
    return render_template('projects/contracts/subcontracts/create.html', project=project, form=form)

@contracts_bp.route('/subcontracts/<int:id>')
@login_required
@project_access_required
def view_subcontract(id):
    subcontract = Subcontract.query.get_or_404(id)
    project = Project.query.get_or_404(subcontract.project_id)
    
    # Get related change orders
    change_orders = ContractChangeOrder.query.filter_by(
        contract_id=id, contract_type='subcontract'
    ).order_by(ContractChangeOrder.created_at.desc()).all()
    
    # Get related documents
    documents = ContractDocument.query.filter_by(
        contract_id=id, contract_type='subcontract'
    ).order_by(ContractDocument.uploaded_at.desc()).all()
    
    return render_template('projects/contracts/subcontracts/view.html', 
                           project=project, 
                           subcontract=subcontract,
                           change_orders=change_orders,
                           documents=documents)

# Professional Service Agreements
@contracts_bp.route('/agreements')
@login_required
@project_access_required
def agreements():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    agreements = ProfessionalServiceAgreement.query.filter_by(project_id=project_id).order_by(
        ProfessionalServiceAgreement.created_at.desc()).all()
    return render_template('projects/contracts/agreements/list.html', project=project, agreements=agreements)

@contracts_bp.route('/agreements/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_agreement():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = AgreementForm()
    
    if form.validate_on_submit():
        agreement = ProfessionalServiceAgreement(
            project_id=project_id,
            agreement_number=form.agreement_number.data or f"PSA-{project_id}-{uuid.uuid4().hex[:6].upper()}",
            title=form.title.data,
            description=form.description.data,
            agreement_type=form.agreement_type.data,
            agreement_value=form.agreement_value.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            company_name=form.company_name.data,
            contact_name=form.contact_name.data,
            contact_email=form.contact_email.data,
            contact_phone=form.contact_phone.data,
            scope_of_services=form.scope_of_services.data,
            rate_schedule=form.rate_schedule.data,
            payment_terms=form.payment_terms.data,
            executed_date=form.executed_date.data,
            signed_by=form.signed_by.data,
            insurance_requirements=form.insurance_requirements.data,
            insurance_expiration=form.insurance_expiration.data,
            status=ContractStatus.ACTIVE if form.executed_date.data else ContractStatus.PENDING,
            revised_value=form.agreement_value.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.agreement_document.data:
            file_path = save_file(
                form.agreement_document.data,
                f'contracts/agreements/{agreement.agreement_number}',
                f'agreement_{uuid.uuid4().hex}'
            )
            if file_path:
                agreement.document_path = file_path
        
        db.session.add(agreement)
        db.session.commit()
        flash('Professional Service Agreement created successfully!', 'success')
        return redirect(url_for('projects.contracts.agreements', project_id=project_id))
    
    return render_template('projects/contracts/agreements/create.html', project=project, form=form)

# Lien Waivers
@contracts_bp.route('/lien_waivers')
@login_required
@project_access_required
def lien_waivers():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    waivers = LienWaiver.query.filter_by(project_id=project_id).order_by(LienWaiver.waiver_date.desc()).all()
    return render_template('projects/contracts/lien_waivers/list.html', project=project, waivers=waivers)

@contracts_bp.route('/lien_waivers/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_lien_waiver():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = LienWaiverForm()
    
    if form.validate_on_submit():
        waiver = LienWaiver(
            project_id=project_id,
            contractor_name=form.contractor_name.data,
            waiver_type=form.waiver_type.data,
            waiver_date=form.waiver_date.data,
            amount=form.amount.data,
            through_date=form.through_date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.waiver_document.data:
            file_path = save_file(
                form.waiver_document.data,
                f'contracts/lien_waivers/{project_id}',
                f'waiver_{uuid.uuid4().hex}'
            )
            if file_path:
                waiver.document_path = file_path
        
        db.session.add(waiver)
        db.session.commit()
        flash('Lien waiver created successfully!', 'success')
        return redirect(url_for('projects.contracts.lien_waivers', project_id=project_id))
    
    return render_template('projects/contracts/lien_waivers/create.html', project=project, form=form)

# Certificates of Insurance
@contracts_bp.route('/certificates_of_insurance')
@login_required
@project_access_required
def certificates_of_insurance():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    certificates = CertificateOfInsurance.query.filter_by(project_id=project_id).order_by(
        CertificateOfInsurance.expiration_date.desc()).all()
    return render_template('projects/contracts/insurance/list.html', project=project, certificates=certificates)

@contracts_bp.route('/certificates_of_insurance/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_certificate_of_insurance():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = InsuranceForm()
    
    if form.validate_on_submit():
        certificate = CertificateOfInsurance(
            project_id=project_id,
            provider_name=form.provider_name.data,
            insured_party=form.insured_party.data,
            policy_number=form.policy_number.data,
            policy_type=form.policy_type.data,
            effective_date=form.effective_date.data,
            expiration_date=form.expiration_date.data,
            coverage_amount=form.coverage_amount.data,
            additional_insured=form.additional_insured.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.insurance_document.data:
            file_path = save_file(
                form.insurance_document.data,
                f'contracts/insurance/{project_id}',
                f'insurance_{uuid.uuid4().hex}'
            )
            if file_path:
                certificate.document_path = file_path
        
        db.session.add(certificate)
        db.session.commit()
        flash('Certificate of insurance created successfully!', 'success')
        return redirect(url_for('projects.contracts.certificates_of_insurance', project_id=project_id))
    
    return render_template('projects/contracts/insurance/create.html', project=project, form=form)

# Letters of Intent
@contracts_bp.route('/letters_of_intent')
@login_required
@project_access_required
def letters_of_intent():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    letters = LetterOfIntent.query.filter_by(project_id=project_id).order_by(LetterOfIntent.issue_date.desc()).all()
    return render_template('projects/contracts/loi/list.html', project=project, letters=letters)

@contracts_bp.route('/letters_of_intent/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_letter_of_intent():
    project_id = request.args.get('project_id', type=int)
    project = Project.query.get_or_404(project_id)
    form = LetterOfIntentForm()
    
    if form.validate_on_submit():
        letter = LetterOfIntent(
            project_id=project_id,
            recipient_name=form.recipient_name.data,
            recipient_company=form.recipient_company.data,
            work_description=form.work_description.data,
            estimated_value=form.estimated_value.data,
            issue_date=form.issue_date.data,
            expiration_date=form.expiration_date.data,
            executed=form.executed.data,
            executed_date=form.executed_date.data,
            converted_to_contract=form.converted_to_contract.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.loi_document.data:
            file_path = save_file(
                form.loi_document.data,
                f'contracts/loi/{project_id}',
                f'loi_{uuid.uuid4().hex}'
            )
            if file_path:
                letter.document_path = file_path
        
        db.session.add(letter)
        db.session.commit()
        flash('Letter of intent created successfully!', 'success')
        return redirect(url_for('projects.contracts.letters_of_intent', project_id=project_id))
    
    return render_template('projects/contracts/loi/create.html', project=project, form=form)

# Change Orders
@contracts_bp.route('/contracts/<int:contract_id>/change_orders/create', methods=['GET', 'POST'])
@login_required
@project_access_required
def create_prime_change_order(contract_id):
    contract = PrimeContract.query.get_or_404(contract_id)
    project = Project.query.get_or_404(contract.project_id)
    form = ChangeOrderForm()
    
    if form.validate_on_submit():
        change_order = ContractChangeOrder(
            project_id=project.id,
            contract_id=contract_id,
            contract_type='prime',
            change_order_number=form.change_order_number.data or f"CO-{contract_id}-{uuid.uuid4().hex[:6].upper()}",
            title=form.title.data,
            description=form.description.data,
            amount=form.amount.data,
            status=form.status.data,
            requested_date=form.requested_date.data,
            approved_date=form.approved_date.data if form.status.data == 'approved' else None,
            approved_by=current_user.id if form.status.data == 'approved' else None,
            time_extension_days=form.time_extension_days.data,
            reason_code=form.reason_code.data,
            created_by=current_user.id
        )
        
        # Handle document upload
        if form.change_order_document.data:
            file_path = save_file(
                form.change_order_document.data,
                f'contracts/prime/{contract.id}/change_orders',
                f'co_{uuid.uuid4().hex}'
            )
            if file_path:
                change_order.document_path = file_path
        
        db.session.add(change_order)
        
        # Update contract value if change order is approved
        if form.status.data == 'approved':
            contract.approved_changes += form.amount.data
            contract.update_revised_value()
        elif form.status.data == 'pending':
            contract.pending_changes += form.amount.data
        
        db.session.commit()
        flash('Change order created successfully!', 'success')
        return redirect(url_for('projects.contracts.view_contract', id=contract_id, project_id=project.id))
    
    return render_template('projects/contracts/change_orders/create.html', 
                          project=project, contract=contract, form=form, contract_type='prime')

# Document uploads
@contracts_bp.route('/document/<path:document_path>')
@login_required
def view_document(document_path):
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path)