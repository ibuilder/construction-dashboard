from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, DateField, SelectField, FloatField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, Length, Email
from datetime import date
from app.models.closeout import WarrantyType, WarrantyStatus

class OMManualForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    equipment_category = StringField('Equipment Category', validators=[Optional(), Length(max=100)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    model_number = StringField('Model Number', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    submission_date = DateField('Submission Date', validators=[Optional()], default=date.today)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
    
    manual_file = FileField('Upload Manual', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip'], 'Only PDF, Word documents, and ZIP archives are allowed')
    ])
    
    submit = SubmitField('Save Manual')

class WarrantyForm(FlaskForm):
    title = StringField('Warranty Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    
    warranty_type = SelectField('Warranty Type', choices=[
        (WarrantyType.STANDARD.value, 'Standard'),
        (WarrantyType.EXTENDED.value, 'Extended'),
        (WarrantyType.LIMITED.value, 'Limited'),
        (WarrantyType.SPECIAL.value, 'Special')
    ], validators=[DataRequired()])
    
    status = SelectField('Status', choices=[
        (WarrantyStatus.ACTIVE.value, 'Active'),
        (WarrantyStatus.PENDING.value, 'Pending'),
        (WarrantyStatus.EXPIRED.value, 'Expired'),
        (WarrantyStatus.VOID.value, 'Void')
    ], validators=[DataRequired()])
    
    # Company information
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    supplier = StringField('Supplier', validators=[Optional(), Length(max=100)])
    contractor = StringField('Contractor', validators=[Optional(), Length(max=100)])
    contact_name = StringField('Contact Name', validators=[Optional(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=50)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=100)])
    
    # Equipment information
    equipment_category = StringField('Equipment Category', validators=[Optional(), Length(max=100)])
    model_number = StringField('Model Number', validators=[Optional(), Length(max=100)])
    serial_number = StringField('Serial Number', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    
    # Date information
    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today)
    end_date = DateField('End Date', validators=[Optional()])
    duration_months = IntegerField('Duration (Months)', validators=[Optional()])
    
    # Terms
    terms_conditions = TextAreaField('Terms & Conditions', validators=[Optional(), Length(max=2000)])
    exclusions = TextAreaField('Exclusions', validators=[Optional(), Length(max=2000)])
    maintenance_requirements = TextAreaField('Maintenance Requirements', validators=[Optional(), Length(max=2000)])
    
    warranty_file = FileField('Warranty Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Only PDF, Word documents, and images are allowed')
    ])
    
    submit = SubmitField('Save Warranty')

class AtticStockForm(FlaskForm):
    material_name = StringField('Material Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    unit_of_measure = StringField('Unit of Measure', validators=[DataRequired(), Length(max=50)])
    
    # Material details
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    product_number = StringField('Product Number', validators=[Optional(), Length(max=100)])
    color = StringField('Color', validators=[Optional(), Length(max=100)])
    spec_section = StringField('Spec Section', validators=[Optional(), Length(max=50)])
    
    # Location and dates
    storage_location = StringField('Storage Location', validators=[DataRequired(), Length(max=200)])
    delivery_date = DateField('Delivery Date', validators=[Optional()])
    turnover_date = DateField('Turnover Date', validators=[Optional()])
    
    # Related contacts
    supplier = StringField('Supplier', validators=[Optional(), Length(max=100)])
    subcontractor = StringField('Subcontractor', validators=[Optional(), Length(max=100)])
    contact_information = TextAreaField('Contact Information', validators=[Optional(), Length(max=500)])
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
    
    image = FileField('Material Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed')
    ])
    
    documentation = FileField('Documentation', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF and Word documents are allowed')
    ])
    
    submit = SubmitField('Save Attic Stock')

class FinalInspectionForm(FlaskForm):
    inspection_type = StringField('Inspection Type', validators=[DataRequired(), Length(max=100)])
    authority = StringField('Authority Having Jurisdiction', validators=[Optional(), Length(max=100)])
    inspector_name = StringField('Inspector Name', validators=[Optional(), Length(max=100)])
    inspection_date = DateField('Inspection Date', validators=[DataRequired()], default=date.today)
    
    result = SelectField('Result', choices=[
        ('pass', 'Pass'),
        ('conditional_pass', 'Conditional Pass'),
        ('fail', 'Fail')
    ], validators=[DataRequired()])
    
    certificate_number = StringField('Certificate Number', validators=[Optional(), Length(max=100)])
    expiration_date = DateField('Expiration Date', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    comments = TextAreaField('Comments', validators=[Optional(), Length(max=2000)])
    
    follow_up_required = BooleanField('Follow-up Required', default=False)
    follow_up_notes = TextAreaField('Follow-up Notes', validators=[Optional(), Length(max=2000)])
    
    certificate_file = FileField('Certificate Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Only PDF, Word documents, and images are allowed')
    ])
    
    submit = SubmitField('Save Inspection')

class AsBuiltDrawingForm(FlaskForm):
    title = StringField('Drawing Title', validators=[DataRequired(), Length(max=255)])
    drawing_number = StringField('Drawing Number', validators=[Optional(), Length(max=100)])
    revision = StringField('Revision', validators=[Optional(), Length(max=20)])
    
    discipline = SelectField('Discipline', choices=[
        ('architectural', 'Architectural'),
        ('structural', 'Structural'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('fire_protection', 'Fire Protection'),
        ('civil', 'Civil'),
        ('landscape', 'Landscape'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    date_received = DateField('Date Received', validators=[Optional()], default=date.today)
    
    prepared_by = StringField('Prepared By', validators=[Optional(), Length(max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    contact_information = TextAreaField('Contact Information', validators=[Optional(), Length(max=500)])
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
    
    drawing_file = FileField('Drawing File', validators=[
        Optional(),
        FileAllowed(['pdf', 'dwg', 'rvt', 'zip'], 'Only PDF, DWG, RVT, and ZIP files are allowed')
    ])
    
    submit = SubmitField('Save Drawing')

class CloseoutDocumentForm(FlaskForm):
    title = StringField('Document Title', validators=[DataRequired(), Length(max=255)])
    
    document_type = SelectField('Document Type', choices=[
        ('substantial_completion', 'Certificate of Substantial Completion'),
        ('final_completion', 'Certificate of Final Completion'),
        ('occupancy_permit', 'Certificate of Occupancy'),
        ('lien_waiver', 'Lien Waiver'),
        ('final_payment', 'Final Payment Application'),
        ('consent_of_surety', 'Consent of Surety'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    document_number = StringField('Document Number', validators=[Optional(), Length(max=100)])
    
    date_issued = DateField('Date Issued', validators=[Optional()])
    date_received = DateField('Date Received', validators=[Optional()], default=date.today)
    
    issued_by = StringField('Issued By', validators=[Optional(), Length(max=100)])
    received_from = StringField('Received From', validators=[Optional(), Length(max=100)])
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
    
    document_file = FileField('Document File', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Only PDF, Word documents, and images are allowed')
    ])
    
    submit = SubmitField('Save Document')