from flask import Blueprint, request, jsonify
from tweet.models import Tweet
from user.models import User, UserRole
from db import db
from auth.utils import decode_jwt, role_required

tweet_blueprint = Blueprint("tweet", __name__)

@tweet_blueprint.route("/create", methods=["POST"])
@role_required(UserRole.USER)
def post_tweet():
    
    payload = decode_jwt(request.headers.get('Authorization'))
    if not payload:
        return jsonify({"error_message": "token tidak valid"}), 401

    user = User.query.get(payload["user_id"])
    if not user:
        return jsonify({"error_message": "User not found!"}), 404

    data = request.get_json()
    tweet_content = data.get("Tweet")
    
    if not tweet_content:
        return jsonify({"error_message": "Tweet tidak boleh kosong"}), 400

    if len(tweet_content) > 150:
        return jsonify({"error_message": "Tweet tidak boleh lebih dari 150 karakter"}), 400


    new_tweet = Tweet(user_id=user.id, content=tweet_content)
    db.session.add(new_tweet)
    db.session.commit()

    return jsonify({
        "id": new_tweet.id,
        "published_at": new_tweet.published_at.isoformat(),
        "tweet": new_tweet.content
    }), 200
