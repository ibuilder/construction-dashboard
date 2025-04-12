from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SafetyObservationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    observation_date = DateField('Observation Date', format='%Y-%m-%d')
    location = StringField('Location', validators=[DataRequired()])
    category = SelectField('Category', choices=[('hazard', 'Hazard'), ('near-miss', 'Near Miss')], validators=[DataRequired()])
    severity = SelectField('Severity', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class IncidentReportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    incident_date = DateField('Incident Date', format='%Y-%m-%d')
    incident_time = StringField('Incident Time')
    location = StringField('Location', validators=[DataRequired()])
    type = SelectField('Type', choices=[('accident', 'Accident'), ('injury', 'Injury')], validators=[DataRequired()])
    severity = SelectField('Severity', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], validators=[DataRequired()])
    reported_by_name = StringField('Reported By Name')
    reported_by_title = StringField('Reported By Title')
    witness_names = StringField('Witness Names')
    root_cause = TextAreaField('Root Cause')
    corrective_actions = TextAreaField('Corrective Actions')
    is_osha_recordable = SelectField('OSHA Recordable', choices=[('yes', 'Yes'), ('no', 'No')])
    is_lost_time = SelectField('Lost Time', choices=[('yes', 'Yes'), ('no', 'No')])
    submit = SubmitField('Submit')