from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class BIMUploadForm(FlaskForm):
    model_file = FileField('Upload IFC Model', validators=[DataRequired()])
    submit = SubmitField('Upload')