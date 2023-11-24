from flask import Blueprint, request
from common.bcrypt import bcrypt
from user.models import User, UserRole
from db import db
import jwt, os
from datetime import datetime, timedelta
from marshmallow import Schema, fields, ValidationError

auth_blp = Blueprint("auth", __name__)

class UserRegistrationSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.Email(required=True)
    bio = fields.String(validate=lambda x: len(x) <= 200)  
    role = fields.String(validate=lambda x: x in [role.value for role in UserRole])

class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    
@auth_blp.route("/registration", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()

    try:
        data = schema.load(data)
    except ValidationError as err:
        return {"error_message": err.messages}, 400

    if User.query.filter_by(username=data['username']).first():
        return {"error_message": "username sudah digunakan"}, 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    role = UserRole[data.get('role', 'USER')]  
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        bio=data.get('bio'),
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    return {
        'user_id': new_user.id,
        'username': new_user.username,
        'bio': new_user.bio
    }, 200



@auth_blp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    schema = UserLoginSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return {"error_message": err.messages}, 400

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error_message": "username atau password tidak tepat"}, 401
    
    if user.is_suspended:
        return {"error_message": "Akun telah di suspend"}, 401
    
    valid_password = bcrypt.check_password_hash(user.password, password)
    if not valid_password:
        return {"error_message": "username atau password tidak tepat"}, 401
    
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
    
    return {
        'token': token
    }, 200

