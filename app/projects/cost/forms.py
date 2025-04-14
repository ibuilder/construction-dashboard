from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, DecimalField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms.fields import FormField, SelectMultipleField
from flask_wtf.file import FileField, FileAllowed  

class BudgetForm(FlaskForm):
    """Form for creating and updating project budgets"""
    version = StringField('Budget Version', validators=[DataRequired()])
    description = TextAreaField('Budget Description', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Budget')

class BudgetItemForm(FlaskForm):
    """Form for adding budget line items"""
    code = StringField('Cost Code', validators=[DataRequired()])
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('general', 'General Requirements'),
        ('sitework', 'Site Work'),
        ('concrete', 'Concrete'),
        ('masonry', 'Masonry'),
        ('metals', 'Metals'),
        ('wood', 'Wood & Plastics'),
        ('thermal', 'Thermal & Moisture Protection'),
        ('doors', 'Doors & Windows'),
        ('finishes', 'Finishes'),
        ('specialties', 'Specialties'),
        ('equipment', 'Equipment'),
        ('furnishings', 'Furnishings'),
        ('special', 'Special Construction'),
        ('conveying', 'Conveying Systems'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    original_amount = DecimalField('Original Amount', validators=[
        DataRequired(), 
        NumberRange(min=0, message='Amount must be positive')
    ])
    committed_cost = DecimalField('Committed Cost', validators=[Optional()])
    projected_cost = DecimalField('Projected Cost', validators=[Optional()])
    submit = SubmitField('Add Budget Item')

class ChangeOrderForm(FlaskForm):
    """Form for creating change orders"""
    number = StringField('Change Order Number', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    reason = TextAreaField('Reason for Change', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    date_issued = DateField('Date Issued', format='%Y-%m-%d', validators=[Optional()])
    date_required = DateField('Decision Required By', format='%Y-%m-%d', validators=[Optional()])
    budget_item_id = SelectField('Budget Item', coerce=int, validators=[Optional()])
    pco_id = HiddenField('Potential Change Order ID')
    attachment = FileField('Attachment', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Only PDF, Word, and images allowed')
    ])
    submit = SubmitField('Submit Change Order')

class PotentialChangeOrderForm(FlaskForm):
    """Form for creating potential change orders"""
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired()])
    estimated_amount = DecimalField('Estimated Amount', validators=[
        DataRequired(), 
        NumberRange(min=0, message='Amount must be positive')
    ])
    date_identified = DateField('Date Identified', format='%Y-%m-%d', validators=[Optional()])
    initiator = SelectField('Initiated By', choices=[
        ('owner', 'Owner'),
        ('architect', 'Architect'),
        ('contractor', 'Contractor'),
        ('subcontractor', 'Subcontractor'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    impact = SelectField('Schedule Impact', choices=[
        ('none', 'None'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major')
    ], default='none')
    budget_item_id = SelectField('Budget Item', coerce=int, validators=[Optional()])
    attachment = FileField('Attachment')
    submit = SubmitField('Submit PCO')

class InvoiceForm(FlaskForm):
    """Form for creating invoices"""
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    vendor = SelectField('Vendor', coerce=int, validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[
        DataRequired(), 
        NumberRange(min=0, message='Amount must be positive')
    ])
    tax_amount = DecimalField('Tax Amount', validators=[Optional()])
    invoice_date = DateField('Invoice Date', format='%Y-%m-%d', validators=[Optional()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    budget_item_id = SelectField('Budget Item', coerce=int, validators=[Optional()])
    contract_id = SelectField('Contract', coerce=int, validators=[Optional()])
    invoice_file = FileField('Upload Invoice', validators=[
        FileAllowed(['pdf', 'jpg', 'png'], 'Only PDF and images allowed')
    ])
    submit = SubmitField('Submit Invoice')

class DirectCostForm(FlaskForm):
    """Form for adding direct costs"""
    description = TextAreaField('Description', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0, message='Amount must be positive')
    ])
    date_incurred = DateField('Date Incurred', format='%Y-%m-%d', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('labor', 'Labor'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('subcontractor', 'Subcontractor'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    budget_item_id = SelectField('Budget Item', coerce=int, validators=[Optional()])
    receipt = FileField('Receipt', validators=[
        FileAllowed(['pdf', 'jpg', 'png'], 'Only PDF and images allowed')
    ])
    submit = SubmitField('Add Cost')