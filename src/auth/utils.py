import jwt, os
from functools import wraps
from flask import request, jsonify
from user.models import UserRole, User
from db import db

def decode_jwt(token):
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"error_message": "Token is tidak ada"}), 401

            payload = decode_jwt(token)
            if not payload:
                return jsonify({"error_message": "Token tidak valid"}), 401

            user_id = payload.get("user_id")
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error_message": "User tidak ditemukan"}), 404

            allowed_roles_enum = [UserRole[role] for role in allowed_roles]

     
            if user.role not in allowed_roles_enum:
                return jsonify({"error_message": "Access denied"}), 403
            return func(*args, **kwargs)
        return wrapped_function
    return decorator
