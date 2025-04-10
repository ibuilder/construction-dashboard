from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class BIMModel(db.Model):
    __tablename__ = 'bim_models'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20))
    model_type = db.Column(db.String(50))  # Architectural, Structural, MEP, etc.
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Float)  # Size in MB
    file_format = db.Column(db.String(20))  # RVT, IFC, NWD, etc.
    upload_date = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='current')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='bim_models')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    comments = db.relationship('Comment', backref='bim_model',
                              primaryjoin="and_(Comment.record_type=='bim_model', "
                                         "Comment.record_id==BIMModel.id)")
    attachments = db.relationship('Attachment', backref='bim_model',
                                 primaryjoin="and_(Attachment.record_type=='bim_model', "
                                            "Attachment.record_id==BIMModel.id)")

class CoordinationIssue(db.Model):
    __tablename__ = 'coordination_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    issue_number = db.Column(db.String(20))
    location = db.Column(db.String(100))
    discipline = db.Column(db.String(50))  # Architectural, Structural, MEP, etc.
    priority = db.Column(db.String(20), default='medium')  # High, Medium, Low
    status = db.Column(db.String(20), default='open')  # Open, In Progress, Closed
    identified_date = db.Column(db.Date, default=func.current_date())
    due_date = db.Column(db.Date)
    resolved_date = db.Column(db.Date)
    assigned_to_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    related_model_id = db.Column(db.Integer, db.ForeignKey('bim_models.id'))
    coordinates_x = db.Column(db.Float)
    coordinates_y = db.Column(db.Float)
    coordinates_z = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='coordination_issues')
    assigned_company = db.relationship('Company', foreign_keys=[assigned_to_company_id])
    assigned_user = db.relationship('User', foreign_keys=[assigned_to_user_id])
    related_model = db.relationship('BIMModel', backref='coordination_issues')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='coordination_issue',
                              primaryjoin="and_(Comment.record_type=='coordination_issue', "
                                         "Comment.record_id==CoordinationIssue.id)")
    attachments = db.relationship('Attachment', backref='coordination_issue',
                                 primaryjoin="and_(Attachment.record_type=='coordination_issue', "
                                            "Attachment.record_id==CoordinationIssue.id)")