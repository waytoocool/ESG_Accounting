from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from app.services.initial_data import create_initial_data
from app.extensions import db, login_manager, mail
from .config import DevelopmentConfig
from .utils.helpers import init_url_versioning, init_caching

# Load environment variables
load_dotenv()

def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_object)

    # Initialize utility helpers
    init_url_versioning(app)
    init_caching(app)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Initialize ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Initialize Redis
    from .services.redis import init_redis
    init_redis(app)

    # Register routes
    from .routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        print(f"Registered blueprint: {blueprint.name}")

    # Initialize database tables
    with app.app_context():
        db.create_all()

        # Import and create initial data if needed
        from .models import User, Entity, Framework, DataPoint, ESGData
        create_initial_data(db, Entity, User)

    # Print all routes for debugging
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, Rule: {rule}")

    return app
