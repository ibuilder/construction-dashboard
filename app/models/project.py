from sqlalchemy import Column, Integer, String, Text
from app.extensions import db
import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    PLANNING = 'planning'
    ACTIVE = 'active'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(64), unique=True, index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default=ProjectStatus.PLANNING.value)
    
    # Dates
    start_date = db.Column(db.Date)
    target_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, 
                         onupdate=datetime.datetime.utcnow)
    
    # Location info
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='USA')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Key project info
    contract_amount = db.Column(db.Float, default=0.0)
    client_name = db.Column(db.String(255))
    client_contact_info = db.Column(db.Text)
    
    # Project type and category
    project_type = db.Column(db.String(100))
    category = db.Column(db.String(100))
    
    # Timestamps and metadata
    archived = db.Column(db.Boolean, default=False)
    
    # Relationships
    users = db.relationship('ProjectUser', back_populates='project', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'contract_amount': self.contract_amount,
            'client_name': self.client_name,
            'project_type': self.project_type,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class ProjectUser(db.Model):
    __tablename__ = 'project_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role = db.Column(db.String(100), default='member')
    
    # Define the relationships
    user = db.relationship('User', back_populates='projects')
    project = db.relationship('Project', back_populates='users')
    
    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='uix_user_project'),)