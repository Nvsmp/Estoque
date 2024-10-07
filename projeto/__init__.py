from flask import Flask, request, jsonify, make_response,send_file
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, current_user
from flask_cors import CORS
from flask_talisman import Talisman
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os, smtplib
#, logging

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY_FLASK')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY_FLASK')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
app.config["DEBUG"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

jwt = JWTManager(app)
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
api = Api(app)

CORS(app, resources={
    r"/api/*": {
        "origins": "*", 
        "methods": ["GET","POST", "PATCH", "DELETE"], 
        "allow_headers": ["Content-Type", "Authorization"]
        }
    })

def sendEmail(conteudo, destino):
  corpo_email = conteudo
  msg = email.message.Message()
  msg['Subject'] = "Assunto"
  msg['From'] = "oldblack26@gmail.com"
  msg['To'] = destino
  password = 'lvngogdfdikkmyqd'
  msg.add_header('Content-Type', 'text/html')
  msg.set_payload(corpo_email)
  s = smtplib.SMTP('smtp.gmail.com: 587')
  s.starttls()
  # Login Credentials for sending the email
  s.login(msg['From'], password)
  s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

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

#app.config["SECRET_KEY"] = os.getenv('SECRET_KEY_FLASK') 
#app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY_FLASK')
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=59)

#jwt = JWTManager(app)
#database = SQLAlchemy(app)
#bcrypt = Bcrypt(app)
#api = Api(app)

#if not app.debug:
#        handler = logging.FileHandler('projeto/error.log')
#        handler.setLevel(logging.ERROR)
#        app.logger.addHandler(handler)

from projeto import routes
