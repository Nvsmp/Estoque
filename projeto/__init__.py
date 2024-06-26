from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, current_user
from flask_cors import CORS
from flask_talisman import Talisman
from datetime import timedelta, datetime
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"

CORS(app, resources={
    r"/api/*": {
        "origins": "*", 
        "methods": ["GET","POST", "PATCH", "DELETE"], 
        "allow_headers": ["Content-Type", "Authorization"]
        }
    })

#opcional
#csp = {
#    'default-src': [
#        "'self'",
#        'cdnjs.cloudflare.com'
#    ],
#    'img-src': '*',
#    'script-src': [
#        "'self'",
#        'cdnjs.cloudflare.com'
#    ],
#}

# Talisman(
#    app,
#    content_security_policy=csp,
#    strict_transport_security=True,
#    strict_transport_security_max_age=31536000,
#    strict_transport_security_include_subdomains=True,
#    strict_transport_security_preload=True,
#    frame_options='DENY',
#    x_xss_protection=True,
# )

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY_FLASK') 
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY_FLASK')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=59)

jwt = JWTManager(app)
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
api = Api(app)

from projeto import routes