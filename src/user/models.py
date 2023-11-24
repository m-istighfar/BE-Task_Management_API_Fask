from enum import Enum
from db import db
from sqlalchemy import Enum as SqlEnum  

class UserRole(Enum):
    USER = 'USER'
    MODERATOR = 'MODERATOR'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    bio = db.Column(db.String(200), nullable=True)  
    role = db.Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    is_suspended = db.Column(db.Boolean, default=False)
