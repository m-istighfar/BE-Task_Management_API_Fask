import os
from flask import Flask
from config import Config
from extensions import mail, limiter
from db import db, db_init
from common.bcrypt import bcrypt
from auth.apis import auth_blp
from admin.apis import admin_blueprint
from task.apis import task_blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)


db.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)
limiter.init_app(app)

SWAGGER_URL = '/swagger'  
API_URL = '/static/swagger.yaml'  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  
    API_URL,
    config={  
        'app_name': "Twitter-like API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(auth_blp, url_prefix="/auth")
app.register_blueprint(task_blueprint, url_prefix="/user")
app.register_blueprint(admin_blueprint, url_prefix="/admin")

# with app.app_context():
#     db_init()
