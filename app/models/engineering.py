from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class RFI(db.Model):
    __tablename__ = 'rfis'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    discipline = db.Column(db.String(50))
    status = db.Column(db.String(20), default='open')
    date_submitted = db.Column(db.Date, default=func.current_date())
    date_required = db.Column(db.Date)
    date_answered = db.Column(db.Date)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    answered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='rfis')
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    responder = db.relationship('User', foreign_keys=[answered_by])
    comments = db.relationship('Comment', backref='rfi',
                              primaryjoin="and_(Comment.record_type=='rfi', "
                                         "Comment.record_id==RFI.id)")
    attachments = db.relationship('Attachment', backref='rfi',
                                 primaryjoin="and_(Attachment.record_type=='rfi', "
                                            "Attachment.record_id==RFI.id)")

class Submittal(db.Model):
    __tablename__ = 'submittals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    specification_section = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    date_submitted = db.Column(db.Date, default=func.current_date())
    date_required = db.Column(db.Date)
    date_returned = db.Column(db.Date)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='submittals')
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    comments = db.relationship('Comment', backref='submittal',
                              primaryjoin="and_(Comment.record_type=='submittal', "
                                         "Comment.record_id==Submittal.id)")
    attachments = db.relationship('Attachment', backref='submittal',
                                 primaryjoin="and_(Attachment.record_type=='submittal', "
                                            "Attachment.record_id==Submittal.id)")

class Drawing(db.Model):
    __tablename__ = 'drawings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    number = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    discipline = db.Column(db.String(50))
    sheet_size = db.Column(db.String(20))
    revision = db.Column(db.String(10))
    revision_date = db.Column(db.Date)
    scale = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='drawings')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    comments = db.relationship('Comment', backref='drawing',
                              primaryjoin="and_(Comment.record_type=='drawing', "
                                         "Comment.record_id==Drawing.id)")
    attachments = db.relationship('Attachment', backref='drawing',
                                 primaryjoin="and_(Attachment.record_type=='drawing', "
                                            "Attachment.record_id==Drawing.id)")

class Specification(db.Model):
    __tablename__ = 'specifications'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    section_number = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    division = db.Column(db.String(50))
    version = db.Column(db.String(10))
    issue_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='specifications')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    comments = db.relationship('Comment', backref='specification',
                              primaryjoin="and_(Comment.record_type=='specification', "
                                         "Comment.record_id==Specification.id)")
    attachments = db.relationship('Attachment', backref='specification',
                                 primaryjoin="and_(Attachment.record_type=='specification', "
                                            "Attachment.record_id==Specification.id)")

class Permit(db.Model):
    __tablename__ = 'permits'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    permit_number = db.Column(db.String(50))
    issuing_authority = db.Column(db.String(100))
    type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    submission_date = db.Column(db.Date)
    approval_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='permits')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='permit',
                              primaryjoin="and_(Comment.record_type=='permit', "
                                         "Comment.record_id==Permit.id)")
    attachments = db.relationship('Attachment', backref='permit',
                                 primaryjoin="and_(Attachment.record_type=='permit', "
                                            "Attachment.record_id==Permit.id)")

class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    meeting_type = db.Column(db.String(50))
    attendees = db.Column(db.Text)
    agenda = db.Column(db.Text)
    minutes = db.Column(db.Text)
    action_items = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='meetings')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='meeting',
                              primaryjoin="and_(Comment.record_type=='meeting', "
                                         "Comment.record_id==Meeting.id)")
    attachments = db.relationship('Attachment', backref='meeting',
                                 primaryjoin="and_(Attachment.record_type=='meeting', "
                                            "Attachment.record_id==Meeting.id)")

class Transmittal(db.Model):
    __tablename__ = 'transmittals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_from_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company_to_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date_sent = db.Column(db.Date, default=func.current_date())
    description = db.Column(db.Text)
    method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='transmittals')
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    company_from = db.relationship('Company', foreign_keys=[company_from_id])
    company_to = db.relationship('Company', foreign_keys=[company_to_id])
    comments = db.relationship('Comment', backref='transmittal',
                              primaryjoin="and_(Comment.record_type=='transmittal', "
                                         "Comment.record_id==Transmittal.id)")
    attachments = db.relationship('Attachment', backref='transmittal',
                                 primaryjoin="and_(Attachment.record_type=='transmittal', "
                                            "Attachment.record_id==Transmittal.id)")