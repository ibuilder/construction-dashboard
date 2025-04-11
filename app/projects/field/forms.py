from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, DateField, BooleanField, TimeField, FormField, FieldList, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError
from datetime import date
from app.models.field import WeatherCondition, WorkStatus

class ManpowerEntryForm(FlaskForm):
    company_name = StringField('Company', validators=[DataRequired(), Length(max=100)])
    trade = StringField('Trade', validators=[Length(max=100)])
    personnel_count = IntegerField('Personnel Count', default=0, validators=[NumberRange(min=0)])
    hours_worked = FloatField('Hours Worked', default=0, validators=[NumberRange(min=0)])
    work_description = TextAreaField('Work Description')

class LaborEntryForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    work_description = StringField('Description of Work', validators=[DataRequired(), Length(max=255)])
    worker_count = IntegerField('Number of Workers', validators=[DataRequired(), NumberRange(min=1)])
    hours_worked = FloatField('Hours Worked', validators=[DataRequired(), NumberRange(min=0.5)])

class EquipmentEntryForm(FlaskForm):
    equipment_type = StringField('Equipment Type', validators=[DataRequired(), Length(max=100)])
    count = IntegerField('Count', validators=[DataRequired(), NumberRange(min=1)])
    hours_used = FloatField('Hours Used', validators=[DataRequired(), NumberRange(min=0)])
    notes = StringField('Notes', validators=[Optional(), Length(max=255)])

class DailyReportForm(FlaskForm):
    """Form for creating/editing daily reports"""
    report_number = StringField('Report Number', validators=[DataRequired(), Length(max=50)])
    report_date = DateField('Report Date', validators=[DataRequired()], default=date.today)
    
    # Weather
    weather_condition = SelectField('Weather Condition', choices=[
        (WeatherCondition.SUNNY.value, 'Sunny'),
        (WeatherCondition.PARTLY_CLOUDY.value, 'Partly Cloudy'),
        (WeatherCondition.CLOUDY.value, 'Cloudy'),
        (WeatherCondition.RAINY.value, 'Rainy'),
        (WeatherCondition.STORMY.value, 'Stormy'),
        (WeatherCondition.SNOWY.value, 'Snowy'),
        (WeatherCondition.FOGGY.value, 'Foggy'),
        ('windy', 'Windy')
    ])
    temperature_low = FloatField('Low Temperature (°F)', validators=[Optional()])
    temperature_high = FloatField('High Temperature (°F)', validators=[Optional()])
    precipitation = FloatField('Precipitation (in)', validators=[Optional(), NumberRange(min=0)])
    wind_speed = FloatField('Wind Speed (mph)', validators=[Optional(), NumberRange(min=0)])
    
    # Site conditions
    site_conditions = TextAreaField('Site Conditions', validators=[Optional(), Length(max=1000)])
    work_status = SelectField('Work Status', choices=[
        (WorkStatus.WORKING.value, 'Working (Normal)'),
        (WorkStatus.DELAYED.value, 'Delayed'),
        (WorkStatus.HALTED.value, 'Halted')
    ])
    delay_reason = TextAreaField('Reason for Delay (if applicable)', validators=[Optional(), Length(max=500)])
    
    # Work summary
    work_summary = TextAreaField('Work Performed', validators=[DataRequired(), Length(max=2000)])
    materials_received = TextAreaField('Materials Received', validators=[Optional(), Length(max=1000)])
    
    # Manpower
    contractor_personnel = IntegerField('Contractor Personnel', validators=[Optional(), NumberRange(min=0)], default=0)
    subcontractor_personnel = IntegerField('Subcontractor Personnel', validators=[Optional(), NumberRange(min=0)], default=0)
    
    # Additional info
    equipment_onsite = TextAreaField('Equipment On Site', validators=[Optional()])
    delays = TextAreaField('Delays/Problems', validators=[Optional()])
    visitors = TextAreaField('Visitors', validators=[Optional()])
    safety_incidents = TextAreaField('Safety Incidents/Observations', validators=[Optional()])
    
    # Issues and notes
    issues = TextAreaField('Issues Encountered', validators=[Optional(), Length(max=1000)])
    notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    
    # Labor entries
    labor_entries = FieldList(FormField(LaborEntryForm), min_entries=1, max_entries=20)
    
    # Equipment entries
    equipment_entries = FieldList(FormField(EquipmentEntryForm), min_entries=0, max_entries=20)
    
    # Photos
    photos = FileField('Upload Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ], render_kw={"multiple": True})
    
    # Submit options
    save_draft = SubmitField('Save Draft')
    submit_report = SubmitField('Submit Report')
    
    def validate_report_date(self, field):
        if field.data > date.today():
            raise ValidationError('Report date cannot be in the future.')

class PhotoUploadForm(FlaskForm):
    """Form for uploading photos"""
    photos = MultipleFileField('Upload Photos', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Upload Photos')

class ProjectPhotoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    photo = FileField('Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    is_featured = BooleanField('Feature on Project Dashboard', default=False)
    submit = SubmitField('Upload Photo')

class WorkActivityForm(FlaskForm):
    """Form for work activities"""
    activity_type = SelectField('Activity Type', choices=[
        ('excavation', 'Excavation'),
        ('foundation', 'Foundation'),
        ('framing', 'Framing'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('drywall', 'Drywall'),
        ('painting', 'Painting'),
        ('flooring', 'Flooring'),
        ('roofing', 'Roofing'),
        ('site_work', 'Site Work'),
        ('concrete', 'Concrete'),
        ('masonry', 'Masonry'),
        ('carpentry', 'Carpentry'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other')
    ])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    percentage_complete = IntegerField('Percentage Complete', validators=[Optional(), NumberRange(min=0, max=100)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Activity')

class FieldPhotoForm(FlaskForm):
    title = StringField('Title', validators=[Length(max=100)])
    description = TextAreaField('Description')
    location = StringField('Location', validators=[Length(max=255)])
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    taken_at = DateField('Date Taken', validators=[Optional()])
    photo = FileField('Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class SafetyIncidentForm(FlaskForm):
    incident_date = DateField('Incident Date', validators=[DataRequired()], default=date.today)
    incident_time = TimeField('Incident Time', validators=[DataRequired()])
    title = StringField('Incident Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=2000)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    severity = SelectField('Severity', choices=[
        ('minor', 'Minor'),
        ('serious', 'Serious'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    incident_type = SelectField('Incident Type', choices=[
        ('near_miss', 'Near Miss'),
        ('first_aid', 'First Aid'),
        ('injury', 'Injury'),
        ('property_damage', 'Property Damage')
    ], validators=[DataRequired()])
    involved_parties = TextAreaField('Involved Parties', validators=[Optional(), Length(max=500)])
    witnesses = TextAreaField('Witnesses', validators=[Optional(), Length(max=500)])
    actions_taken = TextAreaField('Actions Taken', validators=[Optional(), Length(max=1000)])
    photos = FileField('Upload Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ], render_kw={"multiple": True})
    submit = SubmitField('Report Incident')

class PunchlistItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('structural', 'Structural'),
        ('architectural', 'Architectural'),
        ('finishes', 'Finishes'),
        ('site_work', 'Site Work'),
        ('other', 'Other')
    ])
    responsible_party = StringField('Responsible Party', validators=[DataRequired(), Length(max=100)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    due_date = DateField('Due Date', validators=[Optional()])
    photos = FileField('Upload Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ], render_kw={"multiple": True})
    submit = SubmitField('Create Punchlist Item')

class PunchlistStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified')
    ])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')

class FieldInspectionForm(FlaskForm):
    inspection_date = DateField('Inspection Date', validators=[DataRequired()])
    inspection_type = StringField('Inspection Type', validators=[DataRequired(), Length(max=100)])
    inspector = StringField('Inspector Name', validators=[Length(max=100)])
    agency = StringField('Agency', validators=[Length(max=100)])
    result = SelectField('Result', choices=[
        ('pass', 'Pass'),
        ('pass_with_comments', 'Pass with Comments'),
        ('fail', 'Fail')
    ])
    notes = TextAreaField('Notes')
    followup_required = BooleanField('Follow-up Required')
    followup_date = DateField('Follow-up Date', validators=[Optional()])
    attachments = MultipleFileField('Attachments')