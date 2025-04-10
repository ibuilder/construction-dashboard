from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.settings import Company

def company_query():
    return Company.query.filter_by(status='active').order_by(Company.name).all()

class BidderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    company = QuerySelectField('Company', query_factory=company_query, 
                            get_label='name', allow_blank=True)
    contact_name = StringField('Contact Name', validators=[Length(max=100)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[Length(max=20)])
    qualification_date = DateField('Qualification Date', validators=[Optional()])
    qualification_status = SelectField('Status', choices=[
        ('pending', 'Pending Review'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified')
    ])
    notes = TextAreaField('Notes')

class BidPackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    package_number = StringField('Package Number', validators=[DataRequired(), Length(max=30)])
    description = TextAreaField('Description')
    issue_date = DateField('Issue Date', validators=[Optional()])
    due_date = DateField('Due Date', validators=[Optional()])
    estimated_value = FloatField('Estimated Value ($)', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('under_review', 'Under Review'),
        ('awarded', 'Awarded'),
        ('closed', 'Closed')
    ])

class BidManualForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    version = StringField('Version', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    issue_date = DateField('Issue Date', validators=[Optional()])