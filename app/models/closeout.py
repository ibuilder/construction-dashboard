from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class OMManual(db.Model):
    __tablename__ = 'om_manuals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    system = db.Column(db.String(100))
    specification_section = db.Column(db.String(50))
    submitter_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    submission_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')
    approved_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='om_manuals')
    submitter = db.relationship('Company', foreign_keys=[submitter_id])
    approver = db.relationship('User', foreign_keys=[approved_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='om_manual',
                              primaryjoin="and_(Comment.record_type=='om_manual', "
                                         "Comment.record_id==OMManual.id)")
    attachments = db.relationship('Attachment', backref='om_manual',
                                 primaryjoin="and_(Attachment.record_type=='om_manual', "
                                            "Attachment.record_id==OMManual.id)")

class Warranty(db.Model):
    __tablename__ = 'warranties'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    system_covered = db.Column(db.String(100))
    specification_section = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    duration_months = db.Column(db.Integer)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    special_conditions = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='warranties')
    company = db.relationship('Company', foreign_keys=[company_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='warranty',
                              primaryjoin="and_(Comment.record_type=='warranty', "
                                         "Comment.record_id==Warranty.id)")
    attachments = db.relationship('Attachment', backref='warranty',
                                 primaryjoin="and_(Attachment.record_type=='warranty', "
                                            "Attachment.record_id==Warranty.id)")

class AtticStock(db.Model):
    __tablename__ = 'attic_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    specification_section = db.Column(db.String(50))
    quantity = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20))
    location_stored = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date_delivered = db.Column(db.Date)
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending')
    handover_date = db.Column(db.Date)
    owner_representative = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='attic_stocks')
    supplier = db.relationship('Company', foreign_keys=[supplier_id])
    receiver = db.relationship('User', foreign_keys=[received_by])
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='attic_stock',
                              primaryjoin="and_(Comment.record_type=='attic_stock', "
                                         "Comment.record_id==AtticStock.id)")
    attachments = db.relationship('Attachment', backref='attic_stock',
                                 primaryjoin="and_(Attachment.record_type=='attic_stock', "
                                            "Attachment.record_id==AtticStock.id)")