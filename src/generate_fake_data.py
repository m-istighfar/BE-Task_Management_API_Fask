from flask_bcrypt import Bcrypt
from faker import Faker
from app import db, app
from user.models import User, UserRole
from tweet.models import Tweet
from following.models import Following
import random

fake = Faker()
bcrypt = Bcrypt()

def create_fake_users(num_users=30):
    users = []
    for _ in range(num_users):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            password=bcrypt.generate_password_hash("password123").decode('utf-8'),
            bio=fake.text(max_nb_chars=200),
            role=random.choice([UserRole.USER, UserRole.MODERATOR])
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()
    return users
  
def create_fake_tweets(users, num_tweets=200):
    for _ in range(num_tweets):
        tweet = Tweet(
            user_id=random.choice(users).id,
            content=fake.text(max_nb_chars=150),
            is_spam=random.choice([True, False])
        )
        db.session.add(tweet)
    db.session.commit()

def create_fake_followings(users, num_followings=100):
    for _ in range(num_followings):
        follower = random.choice(users)
        following = random.choice(users)
        if follower != following:
            follow = Following(
                user_id=follower.id,
                following_user_id=following.id
            )
            db.session.add(follow)
    db.session.commit()

def generate_fake_data():
    users = create_fake_users()
    create_fake_tweets(users)
    create_fake_followings(users)

if __name__ == "__main__":
    with app.app_context(): 
        generate_fake_data()
