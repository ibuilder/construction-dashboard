from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class PrimeContractForm(FlaskForm):
    contract_number = StringField('Contract Number', validators=[Optional(), Length(max=50)])
    title = StringField('Contract Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    contract_type = SelectField('Contract Type', choices=[
        ('lump_sum', 'Lump Sum'),
        ('cost_plus', 'Cost Plus'),
        ('gmp', 'Guaranteed Maximum Price'),
        ('t_and_m', 'Time and Materials'),
        ('unit_price', 'Unit Price'),
        ('other', 'Other')
    ])
    contract_value = FloatField('Contract Value ($)', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    
    # Client Information
    client_name = StringField('Client Name', validators=[DataRequired(), Length(max=100)])
    client_contact = StringField('Client Contact Person', validators=[Optional(), Length(max=100)])
    client_email = StringField('Client Email', validators=[Optional(), Length(max=100)])
    client_phone = StringField('Client Phone', validators=[Optional(), Length(max=20)])
    
    # Financial terms
    retainage_percent = FloatField('Retainage Percentage', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    payment_terms = StringField('Payment Terms', validators=[Optional(), Length(max=100)])
    
    # Contract execution
    executed_date = DateField('Executed Date', validators=[Optional()])
    signed_by = StringField('Signed By', validators=[Optional(), Length(max=100)])
    
    # File upload
    contract_document = FileField('Contract Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')
    ])
    
    submit = SubmitField('Save Contract')

class SubcontractForm(FlaskForm):
    subcontract_number = StringField('Subcontract Number', validators=[Optional(), Length(max=50)])
    title = StringField('Subcontract Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    subcontract_type = SelectField('Subcontract Type', choices=[
        ('lump_sum', 'Lump Sum'),
        ('unit_price', 'Unit Price'),
        ('t_and_m', 'Time and Materials'),
        ('other', 'Other')
    ])
    subcontract_value = FloatField('Subcontract Value ($)', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    
    # Subcontractor Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    contact_name = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Contact Email', validators=[Optional(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Scope
    scope_of_work = TextAreaField('Scope of Work', validators=[Optional(), Length(max=2000)])
    
    # Financial terms
    retainage_percent = FloatField('Retainage Percentage', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    payment_terms = StringField('Payment Terms', validators=[Optional(), Length(max=100)])
    
    # Execution
    executed_date = DateField('Executed Date', validators=[Optional()])
    signed_by = StringField('Signed By', validators=[Optional(), Length(max=100)])
    
    # Insurance
    insurance_expiration = DateField('Insurance Expiration', validators=[Optional()])
    bonded = BooleanField('Is Bonded?', default=False)
    bond_company = StringField('Bond Company', validators=[Optional(), Length(max=100)])
    
    # File upload
    contract_document = FileField('Contract Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')
    ])
    
    submit = SubmitField('Save Subcontract')

class AgreementForm(FlaskForm):
    agreement_number = StringField('Agreement Number', validators=[Optional(), Length(max=50)])
    title = StringField('Agreement Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    agreement_type = SelectField('Agreement Type', choices=[
        ('hourly', 'Hourly Rate'),
        ('fixed_fee', 'Fixed Fee'),
        ('percentage', 'Percentage Based'),
        ('other', 'Other')
    ])
    agreement_value = FloatField('Agreement Value ($)', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    
    # Service Provider Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    contact_name = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Contact Email', validators=[Optional(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Scope
    scope_of_services = TextAreaField('Scope of Services', validators=[Optional(), Length(max=2000)])
    
    # Financial terms
    rate_schedule = TextAreaField('Rate Schedule', validators=[Optional(), Length(max=1000)])
    payment_terms = StringField('Payment Terms', validators=[Optional(), Length(max=100)])
    
    # Execution
    executed_date = DateField('Executed Date', validators=[Optional()])
    signed_by = StringField('Signed By', validators=[Optional(), Length(max=100)])
    
    # Insurance
    insurance_requirements = TextAreaField('Insurance Requirements', validators=[Optional(), Length(max=1000)])
    insurance_expiration = DateField('Insurance Expiration', validators=[Optional()])
    
    # File upload
    agreement_document = FileField('Agreement Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')
    ])
    
    submit = SubmitField('Save Agreement')

class LienWaiverForm(FlaskForm):
    contractor_name = StringField('Contractor Name', validators=[DataRequired(), Length(max=100)])
    waiver_type = SelectField('Waiver Type', choices=[
        ('partial_conditional', 'Partial Conditional'),
        ('partial_unconditional', 'Partial Unconditional'),
        ('final_conditional', 'Final Conditional'),
        ('final_unconditional', 'Final Unconditional')
    ])
    waiver_date = DateField('Waiver Date', validators=[DataRequired()])
    amount = FloatField('Amount ($)', validators=[Optional(), NumberRange(min=0)])
    through_date = DateField('Through Date', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    
    # File upload
    waiver_document = FileField('Waiver Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Documents or images only!')
    ])
    
    submit = SubmitField('Save Lien Waiver')

class InsuranceForm(FlaskForm):
    provider_name = StringField('Insurance Provider', validators=[DataRequired(), Length(max=100)])
    insured_party = StringField('Insured Party', validators=[DataRequired(), Length(max=100)])
    policy_number = StringField('Policy Number', validators=[DataRequired(), Length(max=50)])
    policy_type = SelectField('Policy Type', choices=[
        ('general_liability', 'General Liability'),
        ('workers_comp', 'Workers Compensation'),
        ('auto', 'Auto Liability'),
        ('umbrella', 'Umbrella/Excess'),
        ('professional', 'Professional Liability'),
        ('builders_risk', 'Builders Risk'),
        ('other', 'Other')
    ])
    effective_date = DateField('Effective Date', validators=[Optional()])
    expiration_date = DateField('Expiration Date', validators=[DataRequired()])
    coverage_amount = FloatField('Coverage Amount ($)', validators=[Optional(), NumberRange(min=0)])
    additional_insured = BooleanField('Additional Insured', default=False)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    
    # File upload
    insurance_document = FileField('Insurance Certificate', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Documents or images only!')
    ])
    
    submit = SubmitField('Save Certificate')

class LetterOfIntentForm(FlaskForm):
    recipient_name = StringField('Recipient Name', validators=[DataRequired(), Length(max=100)])
    recipient_company = StringField('Recipient Company', validators=[Optional(), Length(max=100)])
    work_description = TextAreaField('Description of Work', validators=[DataRequired(), Length(max=2000)])
    estimated_value = FloatField('Estimated Value ($)', validators=[Optional(), NumberRange(min=0)])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    expiration_date = DateField('Expiration Date', validators=[Optional()])
    executed = BooleanField('Executed', default=False)
    executed_date = DateField('Execution Date', validators=[Optional()])
    converted_to_contract = BooleanField('Converted to Contract', default=False)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    
    # File upload
    loi_document = FileField('Letter of Intent Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')
    ])
    
    submit = SubmitField('Save Letter of Intent')

class ChangeOrderForm(FlaskForm):
    change_order_number = StringField('Change Order Number', validators=[Optional(), Length(max=50)])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    amount = FloatField('Amount ($)', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    requested_date = DateField('Request Date', validators=[Optional()], default=lambda: datetime.now())
    approved_date = DateField('Approval Date', validators=[Optional()])
    time_extension_days = FloatField('Time Extension (Days)', validators=[Optional(), NumberRange(min=0)], default=0)
    reason_code = SelectField('Reason Code', choices=[
        ('owner_change', 'Owner Requested Change'),
        ('unforeseen', 'Unforeseen Condition'),
        ('design_error', 'Design Error or Omission'),
        ('value_engineering', 'Value Engineering'),
        ('regulatory', 'Regulatory Requirement'),
        ('schedule', 'Schedule Adjustment'),
        ('other', 'Other')
    ])
    
    # File upload
    change_order_document = FileField('Supporting Documents', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Documents or images only!')
    ])
    
    submit = SubmitField('Save Change Order')