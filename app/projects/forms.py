from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.settings import Company

def get_companies():
    return Company.query.filter_by(status='active').order_by(Company.name).all()

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(max=100)])
    number = StringField('Project Number', validators=[Length(max=50)])
    description = TextAreaField('Description')
    address = StringField('Address', validators=[Length(max=100)])
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    zip_code = StringField('Zip Code', validators=[Length(max=20)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    owner_id = QuerySelectField('Owner', query_factory=get_companies, 
                              get_label='name', allow_blank=True, blank_text='-- Select Owner --')