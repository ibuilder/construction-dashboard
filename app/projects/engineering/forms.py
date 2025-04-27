# app/projects/engineering/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, Email
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.settings import Company
from app.models.user import User
from datetime import datetime, timedelta

def get_companies():
    return Company.query.filter_by(status='active').order_by(Company.name).all()

def get_users():
    return User.query.filter_by(status='active').order_by(User.name).all()

class RFIForm(FlaskForm):
    number = StringField('RFI Number', validators=[DataRequired(), Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    question = TextAreaField('Question', validators=[DataRequired()])
    answer = TextAreaField('Answer')
    discipline = SelectField('Discipline', choices=[
        ('', 'Select Discipline'),
        ('architectural', 'Architectural'),
        ('structural', 'Structural'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('civil', 'Civil'),
        ('landscape', 'Landscape'),
        ('fire_protection', 'Fire Protection'),
        ('other', 'Other')
    ])
    date_required = DateField('Response Required By', validators=[Optional()], 
                            default=datetime.now() + timedelta(days=7))
    
class SubmittalForm(FlaskForm):
    number = StringField('Submittal Number', validators=[DataRequired(), Length(max=20)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    specification_section = StringField('Specification Section', validators=[Length(max=50)])
    date_required = DateField('Response Required By', validators=[Optional()], 
                            default=datetime.now() + timedelta(days=14))

class DrawingForm(FlaskForm):
    number = StringField('Drawing Number', validators=[DataRequired(), Length(max=30)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    discipline = SelectField('Discipline', choices=[
        ('', 'Select Discipline'),
        ('architectural', 'Architectural'),
        ('structural', 'Structural'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('civil', 'Civil'),
        ('landscape', 'Landscape'),
        ('fire_protection', 'Fire Protection'),
        ('other', 'Other')
    ])
    sheet_size = StringField('Sheet Size', validators=[Length(max=20)])
    revision = StringField('Revision', validators=[Length(max=10)])
    revision_date = DateField('Revision Date', validators=[Optional()])
    scale = StringField('Scale', validators=[Length(max=20)])

class SpecificationForm(FlaskForm):
    section_number = StringField('Section Number', validators=[DataRequired(), Length(max=20)])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    division = StringField('Division', validators=[Length(max=50)])
    version = StringField('Version', validators=[Length(max=10)])
    issue_date = DateField('Issue Date', validators=[Optional()])

class PermitForm(FlaskForm):
    name = StringField('Permit Name', validators=[DataRequired(), Length(max=100)])
    permit_number = StringField('Permit Number', validators=[Length(max=50)])
    issuing_authority = StringField('Issuing Authority', validators=[Length(max=100)])
    type = SelectField('Type', choices=[
        ('building', 'Building Permit'),
        ('electrical', 'Electrical Permit'),
        ('plumbing', 'Plumbing Permit'),
        ('mechanical', 'Mechanical Permit'),
        ('fire', 'Fire Permit'),
        ('zoning', 'Zoning Permit'),
        ('environmental', 'Environmental Permit'),
        ('other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('pending', 'Application Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('issued', 'Issued'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ])
    submission_date = DateField('Submission Date', validators=[Optional()])
    approval_date = DateField('Approval Date', validators=[Optional()])
    expiration_date = DateField('Expiration Date', validators=[Optional()])
    notes = TextAreaField('Notes')

class MeetingForm(FlaskForm):
    title = StringField('Meeting Title', validators=[DataRequired(), Length(max=100)])
    meeting_date = DateField('Meeting Date', validators=[DataRequired()], default=datetime.now())
    location = StringField('Location', validators=[Length(max=100)])
    meeting_type = SelectField('Meeting Type', choices=[
        ('progress', 'Progress Meeting'),
        ('coordination', 'Coordination Meeting'),
        ('design', 'Design Meeting'),
        ('pre_construction', 'Pre-Construction Meeting'),
        ('safety', 'Safety Meeting'),
        ('owner', 'Owner Meeting'),
        ('other', 'Other')
    ])
    attendees = TextAreaField('Attendees')
    agenda = TextAreaField('Agenda')
    minutes = TextAreaField('Minutes')
    action_items = TextAreaField('Action Items')

class TransmittalForm(FlaskForm):
    number = StringField('Transmittal Number', validators=[DataRequired(), Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    sender = QuerySelectField('From', query_factory=get_users, 
                            get_label='name', allow_blank=True)
    recipient = QuerySelectField('To', query_factory=get_users, 
                              get_label='name', allow_blank=True)
    company_from = QuerySelectField('From Company', query_factory=get_companies, 
                                  get_label='name', allow_blank=True)
    company_to = QuerySelectField('To Company', query_factory=get_companies, 
                                get_label='name', allow_blank=True)
    description = TextAreaField('Description')
    method = SelectField('Delivery Method', choices=[
        ('email', 'Email'),
        ('mail', 'Mail'),
        ('courier', 'Courier'),
        ('hand', 'Hand Delivery'),
        ('electronic', 'Electronic System'),
        ('other', 'Other')
    ])