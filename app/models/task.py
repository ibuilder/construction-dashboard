from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    title = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')

    project = relationship('Project', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'

    @classmethod
    def create(cls, project_id, title):
        new_task = cls(project_id=project_id, title=title)
        db.session.add(new_task)
        db.session.commit()
        return new_task

    @classmethod
    def read(cls, task_id):
        return cls.query.get(task_id)

    @classmethod
    def update(cls, task_id, title=None, status=None):
        task = cls.query.get(task_id)
        if task:
            if title:
                task.title = title
            if status:
                task.status = status
            db.session.commit()
        return task

    @classmethod
    def delete(cls, task_id):
        task = cls.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
        return task