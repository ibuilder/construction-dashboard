from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date, ForeignKey
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, on_hold
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship('Client', back_populates='projects')
    team_members = relationship('ProjectTeamMember', back_populates='project', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='project', cascade='all, delete-orphan')
    bim_models = relationship('BIMModel', back_populates='project', cascade='all, delete-orphan')
    contracts = relationship('Contract', back_populates='project', cascade='all, delete-orphan')
    
    @property
    def percent_complete(self):
        """Calculate the project completion percentage based on tasks"""
        if not self.tasks:
            return 0
            
        completed_tasks = sum(1 for task in self.tasks if task.status == 'completed')
        return int((completed_tasks / len(self.tasks)) * 100)
    
    @property
    def duration_days(self):
        """Calculate project duration in days"""
        if not self.start_date:
            return 0
            
        end = self.end_date or datetime.utcnow().date()
        return (end - self.start_date).days
    
    @property
    def budget_status(self):
        """Calculate budget status"""
        if not self.budget or self.budget <= 0:
            return 'not_set'
            
        if not self.actual_cost:
            return 'within_budget'
            
        variance = float(self.budget) - float(self.actual_cost)
        variance_percent = (variance / float(self.budget)) * 100
        
        if variance_percent >= 5:
            return 'under_budget'
        elif variance_percent <= -5:
            return 'over_budget'
        else:
            return 'within_budget'