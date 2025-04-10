from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class PrimeContract(db.Model):
    __tablename__ = 'prime_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    contract_number = db.Column(db.String(50))
    contract_type = db.Column(db.String(20))  # GMP, Cost Plus, Lump Sum, CMAR
    owner_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    contractor_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    original_amount = db.Column(db.Numeric(precision=14, scale=2))
    current_amount = db.Column(db.Numeric(precision=14, scale=2))
    execution_date = db.Column(db.Date)
    commencement_date = db.Column(db.Date)
    substantial_completion_date = db.Column(db.Date)
    final_completion_date = db.Column(db.Date)
    contract_term_days = db.Column(db.Integer)
    status = db.Column(db.String(20), default='draft')
    description = db.Column(db.Text)
    special_provisions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='prime_contracts')
    owner = db.relationship('Company', foreign_keys=[owner_id])
    contractor = db.relationship('Company', foreign_keys=[contractor_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='prime_contract',
                              primaryjoin="and_(Comment.record_type=='prime_contract', "
                                         "Comment.record_id==PrimeContract.id)")
    attachments = db.relationship('Attachment', backref='prime_contract',
                                 primaryjoin="and_(Attachment.record_type=='prime_contract', "
                                            "Attachment.record_id==PrimeContract.id)")

class Subcontract(db.Model):
    __tablename__ = 'subcontracts'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subcontract_number = db.Column(db.String(50))
    prime_contract_id = db.Column(db.Integer, db.ForeignKey('prime_contracts.id'))
    contractor_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # General contractor
    subcontractor_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # Subcontractor
    scope_of_work = db.Column(db.Text)
    original_amount = db.Column(db.Numeric(precision=14, scale=2))
    current_amount = db.Column(db.Numeric(precision=14, scale=2))
    execution_date = db.Column(db.Date)
    commencement_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    csi_division = db.Column(db.String(20))
    status = db.Column(db.String(20), default='draft')
    retention_percent = db.Column(db.Numeric(precision=5, scale=2))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='subcontracts')
    prime_contract = db.relationship('PrimeContract', backref='subcontracts')
    contractor = db.relationship('Company', foreign_keys=[contractor_id])
    subcontractor = db.relationship('Company', foreign_keys=[subcontractor_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='subcontract',
                              primaryjoin="and_(Comment.record_type=='subcontract', "
                                         "Comment.record_id==Subcontract.id)")
    attachments = db.relationship('Attachment', backref='subcontract',
                                 primaryjoin="and_(Attachment.record_type=='subcontract', "
                                            "Attachment.record_id==Subcontract.id)")

class ServiceAgreement(db.Model):
    __tablename__ = 'service_agreements'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    agreement_number = db.Column(db.String(50))
    client_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    service_type = db.Column(db.String(50))  # Architecture, Engineering, Consulting, etc.
    scope_of_services = db.Column(db.Text)
    fee_type = db.Column(db.String(20))  # Fixed, Hourly, etc.
    fee_amount = db.Column(db.Numeric(precision=14, scale=2))
    execution_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')
    payment_terms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='service_agreements')
    client = db.relationship('Company', foreign_keys=[client_id])
    provider = db.relationship('Company', foreign_keys=[provider_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='service_agreement',
                              primaryjoin="and_(Comment.record_type=='service_agreement', "
                                         "Comment.record_id==ServiceAgreement.id)")
    attachments = db.relationship('Attachment', backref='service_agreement',
                                 primaryjoin="and_(Attachment.record_type=='service_agreement', "
                                            "Attachment.record_id==ServiceAgreement.id)")

class LienWaiver(db.Model):
    __tablename__ = 'lien_waivers'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    contract_id = db.Column(db.Integer)  # Can be prime_contract_id or subcontract_id
    contract_type = db.Column(db.String(20))  # 'prime' or 'sub'
    waiver_type = db.Column(db.String(20))  # partial, final, conditional, unconditional
    amount = db.Column(db.Numeric(precision=14, scale=2))
    through_date = db.Column(db.Date)
    signed_date = db.Column(db.Date)
    signed_by = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='lien_waivers')
    company = db.relationship('Company', backref='lien_waivers')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='lien_waiver',
                              primaryjoin="and_(Comment.record_type=='lien_waiver', "
                                         "Comment.record_id==LienWaiver.id)")
    attachments = db.relationship('Attachment', backref='lien_waiver',
                                 primaryjoin="and_(Attachment.record_type=='lien_waiver', "
                                            "Attachment.record_id==LienWaiver.id)")

class InsuranceCertificate(db.Model):
    __tablename__ = 'insurance_certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    policy_number = db.Column(db.String(50))
    insurance_type = db.Column(db.String(50))  # General Liability, Workers Comp, etc.
    carrier = db.Column(db.String(100))
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    coverage_amount = db.Column(db.Numeric(precision=14, scale=2))
    additional_insured = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='insurance_certificates')
    company = db.relationship('Company', backref='insurance_certificates')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='insurance_certificate',
                              primaryjoin="and_(Comment.record_type=='insurance_certificate', "
                                         "Comment.record_id==InsuranceCertificate.id)")
    attachments = db.relationship('Attachment', backref='insurance_certificate',
                                 primaryjoin="and_(Attachment.record_type=='insurance_certificate', "
                                            "Attachment.record_id==InsuranceCertificate.id)")

class LetterOfIntent(db.Model):
    __tablename__ = 'letters_of_intent'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    from_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    to_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    reference_number = db.Column(db.String(50))
    scope_of_work = db.Column(db.Text)
    estimated_value = db.Column(db.Numeric(precision=14, scale=2))
    issued_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='issued')
    special_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='letters_of_intent')
    from_company = db.relationship('Company', foreign_keys=[from_company_id])
    to_company = db.relationship('Company', foreign_keys=[to_company_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='letter_of_intent',
                              primaryjoin="and_(Comment.record_type=='letter_of_intent', "
                                         "Comment.record_id==LetterOfIntent.id)")
    attachments = db.relationship('Attachment', backref='letter_of_intent',
                                 primaryjoin="and_(Attachment.record_type=='letter_of_intent', "
                                            "Attachment.record_id==LetterOfIntent.id)")