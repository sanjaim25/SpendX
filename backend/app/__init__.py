from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smartspend_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///smartspend.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '24'))
    )

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
