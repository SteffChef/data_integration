from flask import Flask
from config import Config
from .extensions import db	
from .views import register_blueprints
from flask_cors import CORS
from flask_migrate import Migrate
from app.services.content_based_filtering import ContentBasedFiltering  # Import ContentBasedFiltering

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)  # Add this line

    # Initialize content-based filtering with app context
    with app.app_context():
        cbf = ContentBasedFiltering(db.engine)
        app.cbf = cbf  # Store it in the app

    # Register blueprints
    register_blueprints(app)

    return app