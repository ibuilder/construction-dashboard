from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class DailyReport(db.Model):
    __tablename__ = 'daily_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=func.current_date())
    report_number = db.Column(db.String(20))
    weather_conditions = db.Column(db.String(100))
    temperature_high = db.Column(db.Integer)
    temperature_low = db.Column(db.Integer)
    precipitation = db.Column(db.String(50))
    wind_speed = db.Column(db.String(20))
    delays = db.Column(db.Boolean, default=False)
    delay_description = db.Column(db.Text)
    manpower_count = db.Column(db.Integer, default=0)
    work_performed = db.Column(db.Text)
    materials_received = db.Column(db.Text)
    equipment_used = db.Column(db.Text)
    visitors = db.Column(db.Text)
    safety_incidents = db.Column(db.Text)
    quality_issues = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='daily_reports')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='daily_report',
                              primaryjoin="and_(Comment.record_type=='daily_report', "
                                         "Comment.record_id==DailyReport.id)")
    attachments = db.relationship('Attachment', backref='daily_report',
                                 primaryjoin="and_(Attachment.record_type=='daily_report', "
                                            "Attachment.record_id==DailyReport.id)")
    photos = db.relationship('Photo', backref='daily_report')

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    file_path = db.Column(db.String(255), nullable=False)
    capture_date = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='photos')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    comments = db.relationship('Comment', backref='photo',
                              primaryjoin="and_(Comment.record_type=='photo', "
                                         "Comment.record_id==Photo.id)")

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft')
    file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='schedules')
    creator = db.relationship('User', foreign_keys=[created_by])
    comments = db.relationship('Comment', backref='schedule',
                              primaryjoin="and_(Comment.record_type=='schedule', "
                                         "Comment.record_id==Schedule.id)")
    attachments = db.relationship('Attachment', backref='schedule',
                                 primaryjoin="and_(Attachment.record_type=='schedule', "
                                            "Attachment.record_id==Schedule.id)")

class Checklist(db.Model):
    __tablename__ = 'checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    checklist_type = db.Column(db.String(50))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='open')
    percent_complete = db.Column(db.Integer, default=0)
    due_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='checklists')
    creator = db.relationship('User', foreign_keys=[created_by])
    items = db.relationship('ChecklistItem', backref='checklist', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='checklist',
                              primaryjoin="and_(Comment.record_type=='checklist', "
                                         "Comment.record_id==Checklist.id)")

class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    # Relationships
    completer = db.relationship('User', foreign_keys=[completed_by])

class Punchlist(db.Model):
    __tablename__ = 'punchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='open')
    start_date = db.Column(db.Date, default=func.current_date())
    due_date = db.Column(db.Date)
    percent_complete = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='punchlists')
    creator = db.relationship('User', foreign_keys=[created_by])
    items = db.relationship('PunchlistItem', backref='punchlist', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='punchlist',
                              primaryjoin="and_(Comment.record_type=='punchlist', "
                                         "Comment.record_id==Punchlist.id)")

class PunchlistItem(db.Model):
    __tablename__ = 'punchlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    punchlist_id = db.Column(db.Integer, db.ForeignKey('punchlists.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100))
    responsible_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20), default='medium')
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    verified_date = db.Column(db.Date)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    # Relationships
    responsible_company = db.relationship('Company', foreign_keys=[responsible_company_id])
    verifier = db.relationship('User', foreign_keys=[verified_by])
    photos = db.relationship('PunchlistItemPhoto', backref='punchlist_item', cascade='all, delete-orphan')

class PunchlistItemPhoto(db.Model):
    __tablename__ = 'punchlist_item_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    punchlist_item_id = db.Column(db.Integer, db.ForeignKey('punchlist_items.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    photo_type = db.Column(db.String(20))  # 'before', 'after'
    uploaded_at = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    uploader = db.relationship('User', foreign_keys=[uploaded_by])

class PullPlan(db.Model):
    __tablename__ = 'pull_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(100))
    milestone = db.Column(db.String(100))
    description = db.Column(db.Text)
    facilitator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='planned')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='pull_plans')
    facilitator = db.relationship('User', foreign_keys=[facilitator_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    tasks = db.relationship('PullPlanTask', backref='pull_plan', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='pull_plan',
                              primaryjoin="and_(Comment.record_type=='pull_plan', "
                                         "Comment.record_id==PullPlan.id)")
    attachments = db.relationship('Attachment', backref='pull_plan',
                                 primaryjoin="and_(Attachment.record_type=='pull_plan', "
                                            "Attachment.record_id==PullPlan.id)")

class PullPlanTask(db.Model):
    __tablename__ = 'pull_plan_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    pull_plan_id = db.Column(db.Integer, db.ForeignKey('pull_plans.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)  # in days
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    prerequisites = db.Column(db.Text)
    status = db.Column(db.String(20), default='planned')
    
    # Relationships
    company = db.relationship('Company', foreign_keys=[company_id])
    responsible_user = db.relationship('User', foreign_keys=[responsible_user_id])
    constraints = db.relationship('PullPlanConstraint', backref='task', cascade='all, delete-orphan')

class PullPlanConstraint(db.Model):
    __tablename__ = 'pull_plan_constraints'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('pull_plan_tasks.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    constraint_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])