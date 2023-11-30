
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from user.models import User, UserRole
from task.models import Task
from db import db
from auth.utils import decode_jwt, role_required
from app import bcrypt  
from flask_login import current_user 

admin_blueprint = Blueprint('admin', __name__)

class CreateUserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Str(required=True, validate=lambda x: x.upper() in [role.value for role in UserRole])

class UpdateUserSchema(Schema):
    username = fields.Str()
    email = fields.Email()
    role = fields.Str(validate=lambda x: x.upper() in [role.value for role in UserRole] if x else True)


@admin_blueprint.route('/create-user', methods=['POST'])
@role_required(['ADMIN'])  # Assuming only admins can create users
def create_user():
    schema = CreateUserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'USER')  # Default to 'USER' role if not provided
    verified = True

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or Email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password, role=role, verified=verified)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201

@admin_blueprint.route('/update-user/<int:user_id>', methods=['PUT'])
@role_required(['ADMIN'])
def update_user(user_id):
    schema = UpdateUserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200


@admin_blueprint.route('/delete-user/<int:user_id>', methods=['DELETE'])
@role_required(['ADMIN'])
def delete_user(user_id):
    
    # Decode the JWT from the Authorization header
    token = request.headers.get('Authorization').split()[1]
    current_user_id = decode_jwt(token)['user_id']  # Assuming 'user_id' is in the JWT payload

    if current_user_id == user_id:
        return jsonify({"error": "You cannot delete yourself"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    Task.query.filter_by(userId=user_id).delete()  # Delete related tasks
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User and related tasks deleted successfully"}), 200


@admin_blueprint.route('/list-user', methods=['GET'])
@role_required(['ADMIN'])
def list_users():
    users = User.query.all()
    users_data = []
    for user in users:
        pending_tasks = Task.query.filter_by(userId=user.id, status='pending').count()
        completed_tasks = Task.query.filter_by(userId=user.id, status='completed').count()
        users_data.append({
            "id" : user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name,  # Convert enum to string
            "verified": user.verified,
            "pendingTask": pending_tasks,
            "completedTask": completed_tasks
        })

    return jsonify({"users": users_data}), 200


# Add other routes as needed
