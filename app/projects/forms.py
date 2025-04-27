from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, MultipleFileField, SubmitField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError

from app.models.project import Project, ProjectStatus
from app.models.user import User
from datetime import date

# Project type and category choices
PROJECT_TYPES = [
    ('residential', 'Residential'),
    ('commercial', 'Commercial'),
    ('industrial', 'Industrial'),
    ('infrastructure', 'Infrastructure'),
    ('renovation', 'Renovation')
]

PROJECT_CATEGORIES = [
    ('new_construction', 'New Construction'),
    ('renovation', 'Renovation'),
    ('addition', 'Addition'),
    ('repair', 'Repair'),
    ('maintenance', 'Maintenance')
]

class ProjectForm(FlaskForm):
    """Base form for project creation and editing"""
    name = StringField('Project Name', validators=[DataRequired(), Length(min=3, max=255)])
    number = IntegerField('Project Number', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    
    # Basic info
    status = SelectField('Status', choices=[
        (ProjectStatus.PLANNING.value, 'Planning'),
        (ProjectStatus.ACTIVE.value, 'Active'),
        (ProjectStatus.ON_HOLD.value, 'On Hold'),
        (ProjectStatus.COMPLETED.value, 'Completed'),
        (ProjectStatus.CANCELLED.value, 'Cancelled')
    ], validators=[DataRequired()])

    client_name = StringField('Client Name', validators=[Optional(), Length(max=255)])
    client_contact_info = TextAreaField('Client Contact Information', validators=[Optional(), Length(max=1000)])
    
    # Dates
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    target_completion_date = DateField('Target Completion Date', validators=[Optional()], format='%Y-%m-%d')
    actual_completion_date = DateField('Actual Completion Date', validators=[Optional()], format='%Y-%m-%d')
    
    # Financial
    contract_amount = FloatField('Contract Amount', validators=[Optional(), NumberRange(min=0)])
    
    # Classification
    project_type = SelectField('Project Type', choices=PROJECT_TYPES, validators=[Optional()])
    category = SelectField('Category', choices=PROJECT_CATEGORIES, validators=[Optional()])
    
    # Location
    address = StringField('Address', validators=[Optional(), Length(max=255)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    zip_code = StringField('Zip/Postal Code', validators=[Optional(), Length(max=20)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    
    # Documents
    contract_document = FileField('Contract Document', 
                                validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'PDFs and Word documents only')])
    
    project_images = MultipleFileField('Project Images',
                                    validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only')])
    
    # Team members
    team_members = SelectMultipleField('Team Members', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Save Project')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        # Dynamically populate team members from database
        self.team_members.choices = [(user.id, user.name) for user in User.query.filter_by(is_active=True).order_by(User.name).all()]

    def validate_number(self, field):
        """Ensure project number is unique"""
        project = Project.query.filter_by(number=field.data).first()
        if project and (not hasattr(self, 'project_id') or project.id != self.project_id):
            raise ValidationError('Project number already exists.')
            
    def validate_target_completion_date(self, field):
        """Ensure target completion date is after start date"""
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('Target completion date must be after start date.')
            
    def validate_actual_completion_date(self, field):
        """Ensure actual completion date is after start date"""
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('Actual completion date must be after start date.')


class ProjectTeamForm(FlaskForm):
    """Form for managing project team members"""
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('manager', 'Project Manager'),
        ('member', 'Team Member'),
        ('client', 'Client'),
        ('viewer', 'Viewer')
    ], validators=[DataRequired()])
    submit = SubmitField('Add to Team')


class ProjectFilterForm(FlaskForm):
    """Form for filtering projects on the index page"""
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        (ProjectStatus.PLANNING.value, 'Planning'),
        (ProjectStatus.ACTIVE.value, 'Active'),
        (ProjectStatus.ON_HOLD.value, 'On Hold'),
        (ProjectStatus.COMPLETED.value, 'Completed'),
        (ProjectStatus.CANCELLED.value, 'Cancelled')
    ], validators=[Optional()])
    
    project_type = SelectField('Project Type', choices=[('', 'All Types')] + PROJECT_TYPES, validators=[Optional()])
    search = StringField('Search', validators=[Optional(), Length(max=100)])
    
    sort_by = SelectField('Sort By', choices=[
        ('name', 'Project Name'),
        ('number', 'Project Number'),
        ('start_date', 'Start Date'),
        ('target_completion_date', 'Target Completion Date'),
        ('contract_amount', 'Contract Amount')
    ], default='name')
    
    submit = SubmitField('Apply Filter')


class ProjectNoteForm(FlaskForm):
    """Form for adding a note to a project"""
    content = TextAreaField('Note', validators=[DataRequired(), Length(min=1, max=5000)])