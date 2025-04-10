from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    description = db.Column(db.String(255))
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    # Define role permissions
    PERMISSION = {
        'VIEW': 1,
        'EDIT': 2,
        'CREATE': 4,
        'DELETE': 8,
        'APPROVE': 16,
        'ADMIN': 32
    }
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Role.PERMISSION['VIEW']],
            'Field User': [Role.PERMISSION['VIEW'], Role.PERMISSION['CREATE']],
            'Project Manager': [Role.PERMISSION['VIEW'], Role.PERMISSION['EDIT'], 
                              Role.PERMISSION['CREATE'], Role.PERMISSION['APPROVE']],
            'Admin': [Role.PERMISSION['VIEW'], Role.PERMISSION['EDIT'], 
                    Role.PERMISSION['CREATE'], Role.PERMISSION['DELETE'],
                    Role.PERMISSION['APPROVE'], Role.PERMISSION['ADMIN']]
        }
        
        default_role = 'User'
        
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = sum(roles[r])
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(120))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    api_key = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # User preferences
    preferences = db.Column(db.JSON)
    
    # Relationships
    projects = db.relationship('ProjectUser', back_populates='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'admin@example.com':
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        
        # Generate API key
        if self.api_key is None:
            self.api_key = str(uuid.uuid4())
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_new_api_key(self):
        self.api_key = str(uuid.uuid4())
        return self.api_key
    
    def can(self, permission):
        return self.role is not None and \
            (self.role.permissions & permission) == permission
            
    def is_admin(self):
        return self.can(Role.PERMISSION['ADMIN'])
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role.name,
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    # Notification categories
    daily_reports = db.Column(db.Boolean, default=True)
    rfis = db.Column(db.Boolean, default=True)
    submittals = db.Column(db.Boolean, default=True)
    safety_incidents = db.Column(db.Boolean, default=True)
    punchlist_items = db.Column(db.Boolean, default=True)
    change_orders = db.Column(db.Boolean, default=True)
    project_updates = db.Column(db.Boolean, default=True)
    
    # Delivery method
    push_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notification_preferences', uselist=False))

class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    token = db.Column(db.String(255), nullable=False, index=True)
    platform = db.Column(db.String(20), nullable=False)  # 'ios' or 'android'
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('device_tokens', lazy='dynamic'))