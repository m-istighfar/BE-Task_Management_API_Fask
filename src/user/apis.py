from flask import Blueprint, request, jsonify
from user.models import User, UserRole
from tweet.models import Tweet
from following.models import Following
from db import db
from auth.utils import decode_jwt, role_required

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("profile", methods=["GET"])
@role_required("ALL")
def get_user_profile():
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Token tidak valid"}), 401

    user_id = payload["user_id"]
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error_message": "User not found!"}), 404

 
    tweets = Tweet.query.filter_by(user_id=user_id, is_spam=False).order_by(Tweet.published_at.desc()).limit(10).all()
    tweets_json = [
        {
            "id": tweet.id,
            "published_at": tweet.published_at.isoformat(),
            "tweet": tweet.content
        } for tweet in tweets
    ]

   
    followers_count = Following.query.filter_by(following_user_id=user_id).count()
    following_count = Following.query.filter_by(user_id=user_id).count()

    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "bio": user.bio,
        "tweets": tweets_json,
        "followers": followers_count,
        "following": following_count
    }), 200

@user_blueprint.route("/feed", methods=["GET"])
@role_required(UserRole.USER)
def get_user_feed():
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "Token tidak valid"}), 401

    user_id = payload["user_id"]
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error_message": "User not found!"}), 404

    following_ids = []
    for following in Following.query.filter_by(user_id=user_id).all():
      following_ids.append(following.following_user_id)

  
    tweets = Tweet.query.filter(Tweet.user_id.in_(following_ids), Tweet.is_spam == False).order_by(Tweet.published_at.desc()).limit(10).all()
    tweets_json = [
        {
            "id": tweet.id,
            "user_id": tweet.user_id,
            "username": User.query.get(tweet.user_id).username,
            "published_at": tweet.published_at.isoformat(),
            "tweet": tweet.content
        } for tweet in tweets
    ]

    return jsonify({"tweets": tweets_json}), 200