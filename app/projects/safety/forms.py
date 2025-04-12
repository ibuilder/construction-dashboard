from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, IntegerField, FloatField
from wtforms import BooleanField, SubmitField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from datetime import date
from app.models.safety import ObservationType, IncidentType, SafetySeverity, SafetyStatus

class SafetyObservationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=2000)])
    observation_date = DateField('Observation Date', validators=[Optional()], default=date.today)
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        (ObservationType.UNSAFE_ACT.value, 'Unsafe Act'),
        (ObservationType.UNSAFE_CONDITION.value, 'Unsafe Condition'),
        (ObservationType.ENVIRONMENTAL.value, 'Environmental'),
        (ObservationType.NEAR_MISS.value, 'Near Miss'),
        (ObservationType.SAFETY_VIOLATION.value, 'Safety Violation'),
        (ObservationType.POSITIVE_OBSERVATION.value, 'Positive Observation'),
        (ObservationType.OTHER.value, 'Other')
    ], validators=[DataRequired()])
    severity = SelectField('Severity', choices=[
        (SafetySeverity.LOW.value, 'Low'),
        (SafetySeverity.MEDIUM.value, 'Medium'),
        (SafetySeverity.HIGH.value, 'High'),
        (SafetySeverity.CRITICAL.value, 'Critical')
    ], validators=[DataRequired()])
    corrective_action = TextAreaField('Corrective Action Needed', validators=[Optional(), Length(max=1000)])
    due_date = DateField('Due Date', validators=[Optional()])
    photos = FileField('Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ], render_kw={"multiple": True})
    submit = SubmitField('Submit Observation')

class ObservationStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        (SafetyStatus.OPEN.value, 'Open'),
        (SafetyStatus.IN_PROGRESS.value, 'In Progress'),
        (SafetyStatus.CLOSED.value, 'Closed'),
        (SafetyStatus.VERIFIED.value, 'Verified')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')

class IncidentReportForm(FlaskForm):
    title = StringField('Incident Title', validators=[DataRequired(), Length(max=100)])
    incident_date = DateField('Date of Incident', validators=[DataRequired()], default=date.today)
    incident_time = TimeField('Time of Incident', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description of Incident', validators=[DataRequired(), Length(max=2000)])
    incident_type = SelectField('Incident Type', choices=[
        (IncidentType.NEAR_MISS.value, 'Near Miss'),
        (IncidentType.FIRST_AID.value, 'First Aid'),
        (IncidentType.MEDICAL_TREATMENT.value, 'Medical Treatment'),
        (IncidentType.LOST_TIME.value, 'Lost Time'),
        (IncidentType.FATALITY.value, 'Fatality'),
        (IncidentType.PROPERTY_DAMAGE.value, 'Property Damage'),
        (IncidentType.ENVIRONMENTAL.value, 'Environmental'),
        (IncidentType.VEHICLE.value, 'Vehicle'),
        (IncidentType.OTHER.value, 'Other')
    ], validators=[DataRequired()])
    severity = SelectField('Severity', choices=[
        (SafetySeverity.LOW.value, 'Low'),
        (SafetySeverity.MEDIUM.value, 'Medium'),
        (SafetySeverity.HIGH.value, 'High'),
        (SafetySeverity.CRITICAL.value, 'Critical')
    ], validators=[DataRequired()])

    # Person involved (if injury)
    injured_person = StringField('Name of Injured Person', validators=[Optional(), Length(max=100)])
    injured_person_company = StringField('Company of Injured Person', validators=[Optional(), Length(max=100)])
    body_part = StringField('Body Part Affected', validators=[Optional(), Length(max=50)])
    injury_type = StringField('Type of Injury', validators=[Optional(), Length(max=50)])
    treatment = SelectField('Treatment Required', choices=[
        ('none', 'None'),
        ('first_aid', 'First Aid'),
        ('medical_treatment', 'Medical Treatment'),
        ('hospital', 'Hospital')
    ], validators=[Optional()])
    work_related = BooleanField('Work Related?', default=True)

    # Environmental incident
    spill_type = StringField('Type of Spill/Release', validators=[Optional(), Length(max=100)])
    spill_amount = StringField('Amount Released', validators=[Optional(), Length(max=50)])
    containment_measures = TextAreaField('Containment Measures', validators=[Optional(), Length(max=500)])

    # Property damage
    property_damaged = StringField('Property/Equipment Damaged', validators=[Optional(), Length(max=100)])
    damage_description = TextAreaField('Description of Damage', validators=[Optional(), Length(max=500)])
    estimated_cost = FloatField('Estimated Cost ($)', validators=[Optional(), NumberRange(min=0)])

    # OSHA recordkeeping
    is_recordable = BooleanField('OSHA Recordable?', default=False)
    is_lost_time = BooleanField('Lost Time Incident?', default=False)
    days_restricted = IntegerField('Days on Restricted Duty', validators=[Optional(), NumberRange(min=0)], default=0)
    days_away = IntegerField('Days Away from Work', validators=[Optional(), NumberRange(min=0)], default=0)
    
    # Root cause (can be filled later during investigation)
    immediate_causes = TextAreaField('Immediate Causes', validators=[Optional(), Length(max=1000)])
    root_causes = TextAreaField('Root Causes', validators=[Optional(), Length(max=1000)])
    corrective_actions = TextAreaField('Corrective Actions Needed', validators=[Optional(), Length(max=1000)])

    # Photos
    photos = FileField('Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ], render_kw={"multiple": True})

    save_draft = SubmitField('Save Draft')
    submit = SubmitField('Submit Report')

class JHAStepForm(FlaskForm):
    job_step = TextAreaField('Job Step', validators=[Optional(), Length(max=500)])
    hazards = TextAreaField('Potential Hazards', validators=[Optional(), Length(max=500)])
    controls = TextAreaField('Control Measures', validators=[Optional(), Length(max=500)])

class JobHazardAnalysisForm(FlaskForm):
    title = StringField('JHA Title', validators=[DataRequired(), Length(max=100)])
    job_description = TextAreaField('Job Description', validators=[DataRequired(), Length(max=1000)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    required_ppe = TextAreaField('Required PPE', validators=[Optional(), Length(max=500)])
    required_training = TextAreaField('Required Training', validators=[Optional(), Length(max=500)])
    required_permits = TextAreaField('Required Permits', validators=[Optional(), Length(max=500)])
    special_equipment = TextAreaField('Special Equipment', validators=[Optional(), Length(max=500)])
    approved_by = SelectField('Approved By', coerce=int, validators=[Optional()]) # choices set in view
    steps = FieldList(FormField(JHAStepForm), min_entries=1)
    submit = SubmitField('Submit JHA')

class AttendeeForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    trade = StringField('Trade', validators=[Optional(), Length(max=100)])

class PreTaskPlanForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=100)])
    task_description = TextAreaField('Task Description', validators=[DataRequired(), Length(max=1000)])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    hazards_identified = TextAreaField('Hazards Identified', validators=[DataRequired(), Length(max=1000)])
    safety_concerns = TextAreaField('Safety Concerns', validators=[Optional(), Length(max=500)])
    required_ppe = TextAreaField('Required PPE', validators=[DataRequired(), Length(max=500)])
    tools_equipment = TextAreaField('Tools & Equipment', validators=[Optional(), Length(max=500)])
    emergency_procedures = TextAreaField('Emergency Procedures', validators=[Optional(), Length(max=500)])
    supervisor_name = StringField('Supervisor Name', validators=[DataRequired(), Length(max=100)])
    attendees = FieldList(FormField(AttendeeForm), min_entries=1)
    submit = SubmitField('Submit Pre-Task Plan')

class SafetyOrientationForm(FlaskForm):
    title = StringField('Orientation Title', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    topics = TextAreaField('Topics Covered', validators=[DataRequired(), Length(max=1000)])
    presenter = StringField('Presented By', validators=[DataRequired(), Length(max=100)])
    attendees = FieldList(FormField(AttendeeForm), min_entries=1)
    submit = SubmitField('Submit Safety Orientation')

class SafetyMetricsForm(FlaskForm):
    date = DateField('Month', validators=[DataRequired()], format='%Y-%m')
    man_hours = IntegerField('Man Hours', validators=[DataRequired(), NumberRange(min=0)], default=0)
    recordable_incidents = IntegerField('Recordable Incidents', validators=[Optional(), NumberRange(min=0)], default=0)
    lost_time_incidents = IntegerField('Lost Time Incidents', validators=[Optional(), NumberRange(min=0)], default=0)
    first_aid_incidents = IntegerField('First Aid Incidents', validators=[Optional(), NumberRange(min=0)], default=0)
    near_miss_incidents = IntegerField('Near Miss Incidents', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Submit Metrics')