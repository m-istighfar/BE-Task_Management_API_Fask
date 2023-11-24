from flask import Blueprint, request, jsonify
from tweet.models import Tweet
from db import db
from auth.utils import decode_jwt, role_required
from user.models import User, UserRole
from marshmallow import Schema, fields, ValidationError


moderation_blueprint = Blueprint("moderation", __name__)

class FlagTweetSchema(Schema):
    tweet_id = fields.Int(required=True)
    is_spam = fields.Boolean(missing=True)

class SuspendUserSchema(Schema):
    user_id = fields.Int(required=True)
    is_suspended = fields.Boolean(missing=True)

@moderation_blueprint.route("/tweet", methods=["POST"])
@role_required(UserRole.MODERATOR)
def flag_tweet_as_spam():
    data = request.get_json()
    schema = FlagTweetSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error_message": err.messages}), 400
    
    
    tweet_id = data.get("tweet_id")
    is_spam = data.get("is_spam", True)  

    tweet = Tweet.query.get(tweet_id)
    if not tweet:
        return jsonify({"error_message": "Tweet tidak ditemukan"}), 404

    tweet.is_spam = is_spam
    db.session.commit()

    return jsonify({
        "tweet_id": tweet_id,
        "is_spam": is_spam
    }), 200
    
@moderation_blueprint.route("/user", methods=["POST"])
@role_required(UserRole.MODERATOR)
def suspend_user():
    data = request.get_json()
    schema = SuspendUserSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error_message": err.messages}), 400
    
    user_id = data.get("user_id")
    is_suspended = data.get("is_suspended", True) 
    
    payload = decode_jwt(request.headers.get('Authorization'))
    if payload and payload["user_id"] == user_id:
        return jsonify({"error_message": "Tidak dapat men-suspend akun sendiri"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error_message": "User tidak ditemukan"}), 404

    user.is_suspended = is_suspended
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "is_suspended": is_suspended
    }), 200

