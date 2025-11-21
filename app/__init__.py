from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.login_view = 'auth_api.login_page' # We might need a view for this, or just handle it in frontend

    # Register Blueprints
    from app.routes.auth_api import auth_bp
    from app.routes.rooms_api import rooms_bp
    from app.routes.customers_api import customers_bp
    from app.routes.reservations_api import reservations_bp
    from app.routes.dashboard_api import dashboard_bp
    from app.routes.frontend import frontend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(frontend_bp)

    return app
