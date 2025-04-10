from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    status = db.Column(db.String(20), default='draft')
    total_amount = db.Column(db.Numeric(precision=14, scale=2))
    approved_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='budgets')
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    line_items = db.relationship('BudgetLineItem', backref='budget', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='budget',
                              primaryjoin="and_(Comment.record_type=='budget', "
                                         "Comment.record_id==Budget.id)")
    attachments = db.relationship('Attachment', backref='budget',
                                 primaryjoin="and_(Attachment.record_type=='budget', "
                                            "Attachment.record_id==Budget.id)")

class BudgetLineItem(db.Model):
    __tablename__ = 'budget_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    cost_code_id = db.Column(db.Integer, db.ForeignKey('cost_codes.id'))
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20))
    unit_cost = db.Column(db.Numeric(precision=10, scale=2))
    total_cost = db.Column(db.Numeric(precision=14, scale=2))
    notes = db.Column(db.Text)

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'))
    version = db.Column(db.String(20))
    forecast_date = db.Column(db.Date, default=func.current_date())
    description = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(precision=12, scale=2))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='forecasts')
    budget = db.relationship('Budget', backref='forecasts')
    creator = db.relationship('User', foreign_keys=[created_by])
    line_items = db.relationship('ForecastLineItem', backref='forecast', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='forecast',
                              primaryjoin="and_(Comment.record_type=='forecast', "
                                         "Comment.record_id==Forecast.id)")
    attachments = db.relationship('Attachment', backref='forecast',
                                 primaryjoin="and_(Attachment.record_type=='forecast', "
                                            "Attachment.record_id==Forecast.id)")

class ForecastLineItem(db.Model):
    __tablename__ = 'forecast_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    forecast_id = db.Column(db.Integer, db.ForeignKey('forecasts.id'), nullable=False)
    budget_line_item_id = db.Column(db.Integer, db.ForeignKey('budget_line_items.id'))
    cost_code_id = db.Column(db.Integer, db.ForeignKey('cost_codes.id'))
    description = db.Column(db.String(255), nullable=False)
    current_amount = db.Column(db.Numeric(precision=12, scale=2), default=0)
    projected_amount = db.Column(db.Numeric(precision=12, scale=2), default=0)
    variance_amount = db.Column(db.Numeric(precision=12, scale=2), default=0)
    
    # Relationships
    budget_line_item = db.relationship('BudgetLineItem', backref='forecast_line_items')
    cost_code = db.relationship('CostCode', backref='forecast_line_items')

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    invoice_type = db.Column(db.String(20))  # Progress, Final, etc.
    contract_id = db.Column(db.Integer)  # Can be prime_contract_id or subcontract_id
    contract_type = db.Column(db.String(20))  # 'prime' or 'sub' 
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    amount = db.Column(db.Numeric(precision=14, scale=2), nullable=False)
    tax_amount = db.Column(db.Numeric(precision=10, scale=2))
    total_amount = db.Column(db.Numeric(precision=14, scale=2), nullable=False)
    retention_amount = db.Column(db.Numeric(precision=10, scale=2))
    retention_percent = db.Column(db.Numeric(precision=5, scale=2))
    status = db.Column(db.String(20), default='pending')
    approval_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_date = db.Column(db.Date)
    payment_reference = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='invoices')
    company = db.relationship('Company', backref='invoices')
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    line_items = db.relationship('InvoiceLineItem', backref='invoice', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='invoice',
                              primaryjoin="and_(Comment.record_type=='invoice', "
                                         "Comment.record_id==Invoice.id)")
    attachments = db.relationship('Attachment', backref='invoice',
                                 primaryjoin="and_(Attachment.record_type=='invoice', "
                                            "Attachment.record_id==Invoice.id)")

class InvoiceLineItem(db.Model):
    __tablename__ = 'invoice_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    cost_code_id = db.Column(db.Integer, db.ForeignKey('cost_codes.id'))
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Numeric(precision=10, scale=2))
    total_price = db.Column(db.Numeric(precision=14, scale=2))
    previous_billed = db.Column(db.Numeric(precision=14, scale=2))
    current_billed = db.Column(db.Numeric(precision=14, scale=2))
    percent_complete = db.Column(db.Numeric(precision=5, scale=2))

class DirectCost(db.Model):
    __tablename__ = 'direct_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    cost_type = db.Column(db.String(20))  # Invoice, Certified Payroll, Expense
    reference_number = db.Column(db.String(50))
    description = db.Column(db.String(200), nullable=False)
    cost_code_id = db.Column(db.Integer, db.ForeignKey('cost_codes.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date_incurred = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2), nullable=False)
    tax_amount = db.Column(db.Numeric(precision=10, scale=2))
    status = db.Column(db.String(20), default='pending')
    approved_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    paid_date = db.Column(db.Date)
    payment_reference = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='direct_costs')
    cost_code = db.relationship('CostCode')
    company = db.relationship('Company')
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='direct_cost',
                              primaryjoin="and_(Comment.record_type=='direct_cost', "
                                         "Comment.record_id==DirectCost.id)")
    attachments = db.relationship('Attachment', backref='direct_cost',
                                 primaryjoin="and_(Attachment.record_type=='direct_cost', "
                                            "Attachment.record_id==DirectCost.id)")

class PotentialChangeOrder(db.Model):
    __tablename__ = 'potential_change_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    pco_number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    reason = db.Column(db.Text)
    originator_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date_submitted = db.Column(db.Date)
    estimated_cost = db.Column(db.Numeric(precision=14, scale=2))
    days_impact = db.Column(db.Integer)
    status = db.Column(db.String(20), default='draft')
    rfi_id = db.Column(db.Integer, db.ForeignKey('rfis.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='potential_change_orders')
    originator = db.relationship('Company', foreign_keys=[originator_id])
    rfi = db.relationship('RFI', backref='potential_change_orders')
    creator = db.relationship('User', foreign_keys=[created_by])
    cost_items = db.relationship('PCOCostItem', backref='pco', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='pco',
                              primaryjoin="and_(Comment.record_type=='potential_change_order', "
                                         "Comment.record_id==PotentialChangeOrder.id)")
    attachments = db.relationship('Attachment', backref='pco',
                                 primaryjoin="and_(Attachment.record_type=='potential_change_order', "
                                            "Attachment.record_id==PotentialChangeOrder.id)")

class PCOCostItem(db.Model):
    __tablename__ = 'pco_cost_items'
    
    id = db.Column(db.Integer, primary_key=True)
    pco_id = db.Column(db.Integer, db.ForeignKey('potential_change_orders.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    cost_type = db.Column(db.String(20))  # Labor, Material, Equipment, Subcontractor
    quantity = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20))
    unit_cost = db.Column(db.Numeric(precision=10, scale=2))
    total_cost = db.Column(db.Numeric(precision=14, scale=2))
    notes = db.Column(db.Text)

class ChangeOrder(db.Model):
    __tablename__ = 'change_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    co_number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    contract_id = db.Column(db.Integer)  # Can be prime_contract_id or subcontract_id
    contract_type = db.Column(db.String(20))  # 'prime' or 'sub' 
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    date_issued = db.Column(db.Date)
    amount = db.Column(db.Numeric(precision=14, scale=2), nullable=False)
    days_impact = db.Column(db.Integer)
    status = db.Column(db.String(20), default='draft')
    approval_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='change_orders')
    company = db.relationship('Company', backref='change_orders')
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    pcos = db.relationship('PotentialChangeOrder', secondary='change_order_pcos')
    comments = db.relationship('Comment', backref='change_order',
                              primaryjoin="and_(Comment.record_type=='change_order', "
                                         "Comment.record_id==ChangeOrder.id)")
    attachments = db.relationship('Attachment', backref='change_order',
                                 primaryjoin="and_(Attachment.record_type=='change_order', "
                                            "Attachment.record_id==ChangeOrder.id)")

# Association table for change orders and PCOs
change_order_pcos = db.Table('change_order_pcos',
    db.Column('change_order_id', db.Integer, db.ForeignKey('change_orders.id'), primary_key=True),
    db.Column('pco_id', db.Integer, db.ForeignKey('potential_change_orders.id'), primary_key=True)
)

class ApprovalDocument(db.Model):
    __tablename__ = 'approval_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(20))  # Letter, Directive
    reference_number = db.Column(db.String(50))
    description = db.Column(db.Text)
    from_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    to_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    issue_date = db.Column(db.Date)
    response_due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='issued')
    related_change_order_id = db.Column(db.Integer, db.ForeignKey('change_orders.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='approval_documents')
    from_company = db.relationship('Company', foreign_keys=[from_company_id])
    to_company = db.relationship('Company', foreign_keys=[to_company_id])
    related_change_order = db.relationship('ChangeOrder', backref='approval_documents')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='approval_document',
                              primaryjoin="and_(Comment.record_type=='approval_document', "
                                         "Comment.record_id==ApprovalDocument.id)")
    attachments = db.relationship('Attachment', backref='approval_document',
                                 primaryjoin="and_(Attachment.record_type=='approval_document', "
                                            "Attachment.record_id==ApprovalDocument.id)")

class TimeAndMaterialTicket(db.Model):
    __tablename__ = 't_and_m_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    ticket_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    work_date = db.Column(db.Date, nullable=False)
    work_location = db.Column(db.String(100))
    authorized_by = db.Column(db.String(100))
    status = db.Column(db.String(20), default='submitted')
    related_pco_id = db.Column(db.Integer, db.ForeignKey('potential_change_orders.id'))
    total_labor = db.Column(db.Numeric(precision=12, scale=2))
    total_material = db.Column(db.Numeric(precision=12, scale=2))
    total_equipment = db.Column(db.Numeric(precision=12, scale=2))
    total_amount = db.Column(db.Numeric(precision=12, scale=2))
    approval_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='t_and_m_tickets')
    company = db.relationship('Company', backref='t_and_m_tickets')
    related_pco = db.relationship('PotentialChangeOrder', backref='t_and_m_tickets')
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    labor_items = db.relationship('TMTicketLabor', backref='ticket', cascade='all, delete-orphan')
    material_items = db.relationship('TMTicketMaterial', backref='ticket', cascade='all, delete-orphan')
    equipment_items = db.relationship('TMTicketEquipment', backref='ticket', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='t_and_m_ticket',
                              primaryjoin="and_(Comment.record_type=='t_and_m_ticket', "
                                         "Comment.record_id==TimeAndMaterialTicket.id)")
    attachments = db.relationship('Attachment', backref='t_and_m_ticket',
                                 primaryjoin="and_(Attachment.record_type=='t_and_m_ticket', "
                                            "Attachment.record_id==TimeAndMaterialTicket.id)")

class TMTicketLabor(db.Model):
    __tablename__ = 'tm_ticket_labor'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('t_and_m_tickets.id'), nullable=False)
    worker_name = db.Column(db.String(100), nullable=False)
    labor_type = db.Column(db.String(50))
    rate_id = db.Column(db.Integer, db.ForeignKey('labor_rates.id'))
    hours_regular = db.Column(db.Numeric(precision=5, scale=2))
    hours_overtime = db.Column(db.Numeric(precision=5, scale=2))
    hours_doubletime = db.Column(db.Numeric(precision=5, scale=2))
    rate_regular = db.Column(db.Numeric(precision=8, scale=2))
    rate_overtime = db.Column(db.Numeric(precision=8, scale=2))
    rate_doubletime = db.Column(db.Numeric(precision=8, scale=2))
    total_amount = db.Column(db.Numeric(precision=10, scale=2))
    
    # Relationships
    rate = db.relationship('LaborRate')

class TMTicketMaterial(db.Model):
    __tablename__ = 'tm_ticket_material'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('t_and_m_tickets.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20))
    rate_id = db.Column(db.Integer, db.ForeignKey('material_rates.id'))
    unit_cost = db.Column(db.Numeric(precision=10, scale=2))
    markup_percent = db.Column(db.Numeric(precision=5, scale=2))
    total_amount = db.Column(db.Numeric(precision=12, scale=2))
    
    # Relationships
    rate = db.relationship('MaterialRate')

class TMTicketEquipment(db.Model):
    __tablename__ = 'tm_ticket_equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('t_and_m_tickets.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    equipment_type = db.Column(db.String(50))
    rate_id = db.Column(db.Integer, db.ForeignKey('equipment_rates.id'))
    hours_used = db.Column(db.Numeric(precision=5, scale=2))
    hourly_rate = db.Column(db.Numeric(precision=8, scale=2))
    markup_percent = db.Column(db.Numeric(precision=5, scale=2))
    total_amount = db.Column(db.Numeric(precision=10, scale=2))
    
    # Relationships
    rate = db.relationship('EquipmentRate')