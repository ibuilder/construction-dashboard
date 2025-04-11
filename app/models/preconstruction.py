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
    scope_of_work = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='bid_packages')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_bid_packages')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_bid_packages')
    bidders = db.relationship('QualifiedBidder', secondary='bidders_packages',
                            back_populates='bid_packages')
    comments = db.relationship('Comment', backref='bid_package',
                              primaryjoin="and_(Comment.record_type=='bid_package', "
                                         "Comment.record_id==BidPackage.id)")
    attachments = db.relationship('Attachment', backref='bid_package',
                                 primaryjoin="and_(Attachment.record_type=='bid_package', "
                                            "Attachment.record_id==BidPackage.id)")
    bids = db.relationship('Bid', backref='package')


# Association table for bidders and packages
bidders_packages = db.Table('bidders_packages',
    db.Column('bidder_id', db.Integer, db.ForeignKey('qualified_bidders.id'), primary_key=True),
    db.Column('package_id', db.Integer, db.ForeignKey('bid_packages.id'), primary_key=True),
    db.Column('invited_date', db.DateTime, default=func.now()),
    db.Column('response', db.String(20)),  # accepted, declined, no_response
)


class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('bid_packages.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('qualified_bidders.id'), nullable=False)
    bid_amount = db.Column(db.Numeric(precision=12, scale=2))
    bid_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='received')  # received, under_review, accepted, rejected
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    bidder = db.relationship('QualifiedBidder', backref='bids')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_bids')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_bids')
    comments = db.relationship('Comment', backref='bid',
                              primaryjoin="and_(Comment.record_type=='bid', "
                                         "Comment.record_id==Bid.id)")
    attachments = db.relationship('Attachment', backref='bid',
                                 primaryjoin="and_(Attachment.record_type=='bid', "
                                            "Attachment.record_id==Bid.id)")
                                            
                                            
class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(255))
    tax_id = db.Column(db.String(20))
    company_type = db.Column(db.String(50))  # contractor, subcontractor, supplier, consultant
    trades = db.Column(db.Text)  # Comma-separated list of trades
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_companies')
    contacts = db.relationship('CompanyContact', backref='company', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Company {self.name}>"


class CompanyContact(db.Model):
    __tablename__ = 'company_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    
    def __repr__(self):
        return f"<CompanyContact {self.name}>"