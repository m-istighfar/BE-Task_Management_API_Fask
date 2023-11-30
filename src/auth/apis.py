from flask import Blueprint, request, jsonify
from common.bcrypt import bcrypt
from user.models import User, UserRole
from db import db
import jwt, os
from datetime import datetime, timedelta
from marshmallow import Schema, fields, ValidationError
from flask_mail import Message, Mail
import random
import string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth_blp = Blueprint("auth", __name__)
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

class UserRegistrationSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.Email(required=True)  
    role = fields.String(validate=lambda x: x in [role.value for role in UserRole])

class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

@auth_blp.route("/registration", methods=["POST"])
def register():
    schema = UserRegistrationSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error_message": "Username already in use"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        role=UserRole[data.get('role', 'USER')],
        verification_token=verification_token
    )
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error_message": str(e)}), 500

    send_verification_email(data['email'], verification_token)
    return jsonify({'user_id': new_user.id, 'username': new_user.username}), 201

@auth_blp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"error_message": "Invalid or expired token"}), 400
    
    user.verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully!"}), 200

@auth_blp.route("/login", methods=["POST"])
def login():
    schema = UserLoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error_message": "Invalid username or password"}), 401

    if not user.verified:
        return jsonify({"error_message": "Email not verified"}), 401

    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
    return jsonify({'token': token}), 200

def send_verification_email(email, token):
    verification_link = f"http://yourfrontend.com/verify-email/{token}"
    msg = Message("Email Verification", sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f"Click on the link to verify your email: {verification_link}"
    mail.send(msg)
