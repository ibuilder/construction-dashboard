from wtforms.validators import ValidationError
from app.models.project import Project

class ValidProjectNumber:
    """Validator to check if a project number is valid and not already in use"""
    
    def __init__(self, message=None):
        self.message = message or 'Project number already exists or is invalid.'
    
    def __call__(self, form, field):
        # Check if the project number is valid (alphanumeric with some special chars)
        import re
        if not re.match(r'^[A-Za-z0-9\-\_\.]+$', field.data):
            raise ValidationError('Project number can only contain letters, numbers, hyphens, underscores, and periods.')
        
        # If this is an edit form, we need to check if the number belongs to another project
        if hasattr(form, 'id') and form.id.data:
            project = Project.query.filter_by(number=field.data).first()
            if project and str(project.id) != form.id.data:
                raise ValidationError(self.message)
        else:
            # For new projects, check if the number exists
            project = Project.query.filter_by(number=field.data).first()
            if project:
                raise ValidationError(self.message)