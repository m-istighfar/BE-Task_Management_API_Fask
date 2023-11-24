from db import db
from datetime import datetime



class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(150), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_spam = db.Column(db.Boolean, default=False)
