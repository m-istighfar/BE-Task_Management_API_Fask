from flask import Blueprint, request, jsonify
from app import db, bcrypt, mail, limiter
from flask_mail import Message
from user.models import User, UserRole
from marshmallow import Schema, fields, ValidationError
import jwt
import os
from datetime import datetime, timedelta
import random
import string
import hashlib

auth_blp = Blueprint("auth", __name__)


# Schemas
class UserRegistrationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.String(validate=lambda x: x.lower() in [role.value for role in UserRole])

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    
class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    new_password = fields.Str(required=True)

# Routes
@auth_blp.route("/register", methods=["POST"])
def register():
    schema = UserRegistrationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    verification_token = hashlib.sha256(os.urandom(32)).hexdigest()
    
    role_enum = UserRole[data.get('role', 'USER').upper()]

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        role= role_enum,
        verification_token=verification_token,
        verified=False
    )

    db.session.add(new_user)
    db.session.commit()

    send_verification_email(data['email'], verification_token)
    return jsonify({"message": "User registered successfully. Please check your email to verify your account."}), 201

@auth_blp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    user.verified = True
    user.verification_token = None
    db.session.commit()
    return jsonify({"message": "Account verified successfully"}), 200

@auth_blp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    schema = UserLoginSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    if not user.verified:
        return jsonify({"error": "Email not verified"}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, os.getenv('SECRET_KEY'), algorithm='HS256')

    return jsonify({"token": token}), 200

# Helper functions
def send_verification_email(email, token):
    verification_link = f"http://yourfrontend.com/verify-email/{token}"
    msg = Message("Email Verification", sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f"Click on the link to verify your email: {verification_link}"
    mail.send(msg)

# Add other routes for password reset as needed
@auth_blp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    schema = PasswordResetRequestSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(email=data['email']).first()
    if user:
        reset_token = hashlib.sha256(os.urandom(32)).hexdigest()
        user.reset_password_token = reset_token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        send_password_reset_email(data['email'], reset_token)

    return jsonify({"message": "If the email is associated with an account, a password reset link will be sent."}), 200

@auth_blp.route("/reset-password/<reset_token>", methods=["POST"])
def reset_password(reset_token):
    schema = PasswordResetSchema()
    try:
        data = schema.load(request.json)
        data['reset_token'] = reset_token
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Find the user with the reset token and check if the token is still valid
    user = User.query.filter(User.reset_password_token == reset_token,
                             User.reset_password_expires > datetime.utcnow()).first()
    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Hash the new password and update the user's record
    hashed_password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    user.password = hashed_password
    user.reset_password_token = None
    user.reset_password_expires = None
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200



# Helper functions
def send_password_reset_email(email, reset_token):
    reset_link = f"http://yourfrontend.com/reset-password/{reset_token}"
    msg = Message("Password Reset", sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    msg.body = f"To reset your password, click the following link: {reset_link}"
    mail.send(msg)
