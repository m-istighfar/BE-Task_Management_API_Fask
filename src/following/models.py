from db import db


class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
