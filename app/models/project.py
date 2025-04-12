from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date, ForeignKey
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func

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
    schedules = relationship('Schedule', back_populates='project', cascade='all, delete-orphan')
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
    
    @property
    def days_remaining(self):
        """Calculate remaining days until project end date"""
        if not self.end_date:
            return None
            
        today = datetime.utcnow().date()
        remaining = (self.end_date - today).days
        return remaining if remaining >= 0 else 0
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if not self.end_date:
            return False
            
        today = datetime.utcnow().date()
        return today > self.end_date and self.status != 'completed'
    
    @hybrid_property
    def active_team_count(self):
        """Count active team members"""
        return len([m for m in self.team_members if m.is_active])
    
    @active_team_count.expression
    def active_team_count(cls):
        """SQL expression for active team count"""
        return select(func.count(ProjectTeamMember.id)).\
            where(ProjectTeamMember.project_id == cls.id).\
            where(ProjectTeamMember.is_active == True).\
            label("active_team_count")

class ProjectTeamMember(db.Model):
    __tablename__ = 'project_team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # project_manager, engineer, architect, etc.
    is_active = db.Column(db.Boolean, default=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='team_members')
    user = db.relationship('User', foreign_keys=[user_id], backref='project_memberships')
    added_by_user = db.relationship('User', foreign_keys=[added_by])
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='uix_project_user'),
    )