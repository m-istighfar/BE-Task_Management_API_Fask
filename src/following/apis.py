from flask import Blueprint, request, jsonify
from following.models import Following
from db import db
from auth.utils import decode_jwt, role_required
from user.models import User, UserRole
from marshmallow import Schema, fields, ValidationError



following_blueprint = Blueprint("following", __name__)

class FollowUnfollowSchema(Schema):
    user_id = fields.Int(required=True)

@following_blueprint.route("", methods=["POST"])
@role_required(["USER"])
def manage_following():

    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "token tidak valid"}), 401
    
    data = request.get_json()
    schema = FollowUnfollowSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error_message": err.messages}), 400

    user_id = payload["user_id"]
    target_user_id = data.get("user_id")

    user = User.query.get(target_user_id)
    if not user:
        return jsonify({"error_message": "User tidak ditemukan"}), 404

    if user_id == target_user_id:
        return jsonify({"error_message": "Tidak bisa follow diri sendiri"}), 400

    following = Following.query.filter_by(user_id=user_id, following_user_id=target_user_id).first()

    if following:
        db.session.delete(following)
        db.session.commit()
        following_status = "unfollow"
    else:
        new_following = Following(user_id=user_id, following_user_id=target_user_id)
        db.session.add(new_following)
        db.session.commit()
        following_status = "follow"

    return jsonify({"following_status": following_status}), 200
