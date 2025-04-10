from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class SafetyObservation(db.Model):
    __tablename__ = 'safety_observations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    observation_date = db.Column(db.Date, nullable=False, default=func.current_date())
    location = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    observation_type = db.Column(db.String(50))  # positive, negative, etc.
    risk_level = db.Column(db.String(20))  # high, medium, low
    status = db.Column(db.String(20), default='open')
    corrective_action = db.Column(db.Text)
    due_date = db.Column(db.Date)
    closed_date = db.Column(db.Date)
    closed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='safety_observations')
    creator = db.relationship('User', foreign_keys=[created_by])
    closer = db.relationship('User', foreign_keys=[closed_by])
    company = db.relationship('Company', foreign_keys=[company_id])
    comments = db.relationship('Comment', backref='safety_observation',
                              primaryjoin="and_(Comment.record_type=='safety_observation', "
                                         "Comment.record_id==SafetyObservation.id)")
    attachments = db.relationship('Attachment', backref='safety_observation',
                                 primaryjoin="and_(Attachment.record_type=='safety_observation', "
                                            "Attachment.record_id==SafetyObservation.id)")

class PreTaskPlan(db.Model):
    __tablename__ = 'pre_task_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_date = db.Column(db.Date, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    hazards_identified = db.Column(db.Text)
    safety_measures = db.Column(db.Text)
    required_ppe = db.Column(db.Text)
    tools_equipment = db.Column(db.Text)
    first_aid_location = db.Column(db.String(100))
    emergency_procedures = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    foreman_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='pre_task_plans')
    company = db.relationship('Company', foreign_keys=[company_id])
    foreman = db.relationship('User', foreign_keys=[foreman_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    workers = db.relationship('PreTaskPlanWorker', backref='pre_task_plan', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='pre_task_plan',
                              primaryjoin="and_(Comment.record_type=='pre_task_plan', "
                                         "Comment.record_id==PreTaskPlan.id)")
    attachments = db.relationship('Attachment', backref='pre_task_plan',
                                 primaryjoin="and_(Attachment.record_type=='pre_task_plan', "
                                            "Attachment.record_id==PreTaskPlan.id)")

class PreTaskPlanWorker(db.Model):
    __tablename__ = 'pre_task_plan_workers'
    
    id = db.Column(db.Integer, primary_key=True)
    pre_task_plan_id = db.Column(db.Integer, db.ForeignKey('pre_task_plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    signature = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.DateTime)

class JobHazardAnalysis(db.Model):
    __tablename__ = 'job_hazard_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    jha_number = db.Column(db.String(20))
    task = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    description = db.Column(db.Text)
    personal_protective_equipment = db.Column(db.Text)
    training_required = db.Column(db.Text)
    tools_equipment = db.Column(db.Text)
    permits_required = db.Column(db.Text)
    reference_documents = db.Column(db.Text)
    prepared_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='job_hazard_analyses')
    company = db.relationship('Company', foreign_keys=[company_id])
    preparer = db.relationship('User', foreign_keys=[prepared_by])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    steps = db.relationship('JHAStep', backref='jha', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='jha',
                              primaryjoin="and_(Comment.record_type=='job_hazard_analysis', "
                                         "Comment.record_id==JobHazardAnalysis.id)")
    attachments = db.relationship('Attachment', backref='jha',
                                 primaryjoin="and_(Attachment.record_type=='job_hazard_analysis', "
                                            "Attachment.record_id==JobHazardAnalysis.id)")

class JHAStep(db.Model):
    __tablename__ = 'jha_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    jha_id = db.Column(db.Integer, db.ForeignKey('job_hazard_analyses.id'), nullable=False)
    step_number = db.Column(db.Integer)
    task_step = db.Column(db.String(255), nullable=False)
    hazards = db.Column(db.Text, nullable=False)
    controls = db.Column(db.Text, nullable=False)

class EmployeeOrientation(db.Model):
    __tablename__ = 'employee_orientations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date_of_orientation = db.Column(db.Date, nullable=False)
    employee_signature = db.Column(db.Boolean, default=False)
    trade = db.Column(db.String(50))
    emergency_contact = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    orientation_conducted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    topics_covered = db.Column(db.Text)
    badge_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='employee_orientations')
    company = db.relationship('Company', foreign_keys=[company_id])
    conductor = db.relationship('User', foreign_keys=[orientation_conducted_by])
    certifications = db.relationship('EmployeeCertification', backref='orientation', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='employee_orientation',
                              primaryjoin="and_(Comment.record_type=='employee_orientation', "
                                         "Comment.record_id==EmployeeOrientation.id)")
    attachments = db.relationship('Attachment', backref='employee_orientation',
                                 primaryjoin="and_(Attachment.record_type=='employee_orientation', "
                                            "Attachment.record_id==EmployeeOrientation.id)")

class EmployeeCertification(db.Model):
    __tablename__ = 'employee_certifications'
    
    id = db.Column(db.Integer, primary_key=True)
    orientation_id = db.Column(db.Integer, db.ForeignKey('employee_orientations.id'), nullable=False)
    certification_type = db.Column(db.String(100), nullable=False)
    certificate_number = db.Column(db.String(50))
    issue_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    issuing_authority = db.Column(db.String(100))
    verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_date = db.Column(db.Date)
    
    # Relationships
    verifier = db.relationship('User', foreign_keys=[verified_by])