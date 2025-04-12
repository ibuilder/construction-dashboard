from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length

class BIMUploadForm(FlaskForm):
    name = StringField('Model Name', validators=[DataRequired(), Length(max=255)])
    model_type = SelectField('Model Type', choices=[
        ('architectural', 'Architectural'),
        ('structural', 'Structural'),
        ('mep', 'MEP (Mechanical, Electrical, Plumbing)'),
        ('coordination', 'Coordination'),
        ('fabrication', 'Fabrication'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    file = FileField('IFC File', validators=[
        FileRequired(),
        FileAllowed(['ifc'], 'IFC files only!')
    ])
    notes = TextAreaField('Version Notes')