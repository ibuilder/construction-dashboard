from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BIMModel(db.Model):
    __tablename__ = 'bim_models'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, project_id, file_path):
        self.project_id = project_id
        self.file_path = file_path

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, model_id):
        return cls.query.get(model_id)

    @classmethod
    def get_all_by_project(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()