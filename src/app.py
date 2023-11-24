import os
from flask import Flask
from db import db, db_init
from common.bcrypt import bcrypt
from auth.apis import auth_blp
from user.apis import user_blueprint
from tweet.apis import tweet_blueprint
from following.apis import following_blueprint
from moderation.apis import moderation_blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/swagger'  
API_URL = '/static/swagger.yaml'  

# Blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  
    API_URL,
    config={  
        'app_name': "Twitter-like API"
    }
)




app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(auth_blp, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(tweet_blueprint, url_prefix="/tweet")
app.register_blueprint(following_blueprint, url_prefix="/following")
app.register_blueprint(moderation_blueprint, url_prefix="/moderation")

# with app.app_context():
#     db_init()
