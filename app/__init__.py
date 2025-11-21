# app/__init__.py

from flask import Flask
from .extensions import db, login_manager, bcrypt
from .config import Config
from dotenv import load_dotenv
from flask_login import current_user
import os

def create_app():
    # Load .env if present
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'frontend.admin_login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Make current_user available in all templates
    app.jinja_env.globals['current_user'] = current_user

    # Register blueprints
    from .routes.auth_api import auth_bp
    from .routes.rooms_api import rooms_bp
    from .routes.reservations_api import reservations_bp
    from .routes.dashboard_api import dashboard_bp
    from .routes.frontend import frontend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(frontend_bp)

    return app
