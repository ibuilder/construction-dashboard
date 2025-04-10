from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class QualifiedBidder(db.Model):
    __tablename__ = 'qualified_bidders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    qualification_date = db.Column(db.Date)
    qualification_status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='qualified_bidders')
    company = db.relationship('Company', backref='bidder_qualifications')
    comments = db.relationship('Comment', backref='qualified_bidder', 
                              primaryjoin="and_(Comment.record_type=='qualified_bidder', "
                                         "Comment.record_id==QualifiedBidder.id)")
    attachments = db.relationship('Attachment', backref='qualified_bidder',
                                 primaryjoin="and_(Attachment.record_type=='qualified_bidder', "
                                            "Attachment.record_id==QualifiedBidder.id)")
    bid_packages = db.relationship('BidPackage', secondary='bidders_packages', 
                                  back_populates='bidders')

class BidPackage(db.Model):
    __tablename__ = 'bid_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    package_number = db.Column(db.String(30))
    description = db.Column(db.Text)
    issue_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    estimated_value = db.Column(db.Numeric(precision=12, scale=2))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='bid_packages')
    comments = db.relationship('Comment', backref='bid_package',
                              primaryjoin="and_(Comment.record_type=='bid_package', "
                                         "Comment.record_id==BidPackage.id)")
    attachments = db.relationship('Attachment', backref='bid_package',
                                 primaryjoin="and_(Attachment.record_type=='bid_package', "
                                            "Attachment.record_id==BidPackage.id)")
    bidders = db.relationship('QualifiedBidder', secondary='bidders_packages',
                             back_populates='bid_packages')

# Association table for bidders and packages
bidders_packages = db.Table('bidders_packages',
    db.Column('bidder_id', db.Integer, db.ForeignKey('qualified_bidders.id'), primary_key=True),
    db.Column('package_id', db.Integer, db.ForeignKey('bid_packages.id'), primary_key=True)
)

class BidManual(db.Model):
    __tablename__ = 'bid_manuals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    description = db.Column(db.Text)
    issue_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='bid_manuals')
    comments = db.relationship('Comment', backref='bid_manual',
                              primaryjoin="and_(Comment.record_type=='bid_manual', "
                                         "Comment.record_id==BidManual.id)")
    attachments = db.relationship('Attachment', backref='bid_manual',
                                 primaryjoin="and_(Attachment.record_type=='bid_manual', "
                                            "Attachment.record_id==BidManual.id)")