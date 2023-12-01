from db import db
from sqlalchemy import DateTime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Enum("high", "medium", "low", name="priority_types"), default="medium")
    dueDate = db.Column(DateTime, nullable=True)
    status = db.Column(db.Enum("pending", "completed", name="status_types"), default="pending")
    createdAt = db.Column(DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "dueDate": self.dueDate.isoformat() if self.dueDate else None,
            "status": self.status,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
            "userId": self.userId
        }
