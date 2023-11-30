from flask import Blueprint, request, jsonify
from user.models import User
from task.models import Task
from db import db
from auth.utils import decode_jwt, role_required
from sqlalchemy import or_, and_
from datetime import datetime

task_blueprint = Blueprint("task", __name__)

@task_blueprint.route("/tasks", methods=["GET"])
@role_required(["USER"])
def get_all_tasks():
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    user_id = payload["user_id"]
    args = request.args
    search = args.get('search')
    priority = args.get('priority')
    status = args.get('status')
    due_date = args.get('dueDate')
    sort_order = args.get('sortOrder', 'asc')

    query = Task.query.filter(Task.userId == user_id)

    if search:
        search_query = or_(Task.title.ilike(f'%{search}%'), Task.description.ilike(f'%{search}%'))
        query = query.filter(search_query)

    if priority:
        query = query.filter(Task.priority == priority)

    if status:
        query = query.filter(Task.status == status)

    if due_date:
        query = query.filter(Task.dueDate == datetime.strptime(due_date, '%Y-%m-%d'))

    if sort_order == 'desc':
        query = query.order_by(Task.dueDate.desc())
    else:
        query = query.order_by(Task.dueDate.asc())

    tasks = query.all()
    count = query.count()

    if not tasks:
        message = "No tasks found with the given criteria." if search or priority or status or due_date else "You have no tasks at the moment."
        return jsonify({"message": message, "count": count}), 200

    return jsonify({"message": "Tasks fetched successfully!", "tasks": [task.serialize() for task in tasks], "count": count}), 200


@task_blueprint.route("/tasks/<int:task_id>", methods=["GET"])
@role_required(["USER"])
def get_task_by_id(task_id):
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    task = Task.query.filter_by(id=task_id, userId=payload["user_id"]).first()
    if not task:
        return jsonify({"error_message": "Task not found"}), 404

    return jsonify({"message": "Task fetched successfully!", "task": task.serialize()}), 200

@task_blueprint.route("/tasks", methods=["POST"])
@role_required(["USER"])
def create_task():
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    data = request.get_json()
    new_task = Task(userId=payload["user_id"], **data)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created successfully!", "task": new_task.serialize()}), 201

@task_blueprint.route("/tasks/<int:task_id>", methods=["PUT"])
@role_required(["USER"])
def update_task(task_id):
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    task = Task.query.filter_by(id=task_id, userId=payload["user_id"]).first()
    if not task:
        return jsonify({"error_message": "Task not found"}), 404

    if task.status == "completed":
        return jsonify({"error_message": "Cannot update a task that's already completed"}), 400

    data = request.get_json()
    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()

    return jsonify({"message": "Task updated successfully!", "task": task.serialize()}), 200

@task_blueprint.route("/tasks/<int:task_id>", methods=["DELETE"])
@role_required(["USER"])
def delete_task(task_id):
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    task = Task.query.filter_by(id=task_id, userId=payload["user_id"]).first()
    if not task:
        return jsonify({"error_message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully!"}), 200

@task_blueprint.route("/tasks/delete-all", methods=["DELETE"])
@role_required(["USER"])
def delete_all_tasks():
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    Task.query.filter_by(userId=payload["user_id"]).delete()
    db.session.commit()

    return jsonify({"message": "All tasks deleted successfully!"}), 200

@task_blueprint.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
@role_required(["USER"])
def mark_complete(task_id):
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Invalid token"}), 401

    task = Task.query.filter_by(id=task_id, userId=payload["user_id"]).first()
    if not task:
        return jsonify({"error_message": "Task not found"}), 404

    if task.status == "completed":
        return jsonify({"error_message": "Task is already marked as completed"}), 400

    task.status = "completed"
    db.session.commit()

    return jsonify({"message": "Task marked as completed successfully!", "task": task.serialize()}), 200
