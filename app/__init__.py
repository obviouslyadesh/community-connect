# app/__init__.py - Application factory
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# In create_app() function:
def create_app(config_class='config.Config'):
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config_class)
    
    # Fix PostgreSQL URL
    if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
            'postgres://', 'postgresql://', 1
        )
    
    # Initialize with minimal settings
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import blueprints only when needed
    @app.before_first_request
    def setup_blueprints():
        from app.auth import auth as auth_bp
        from app.routes import main as main_bp
        from app.oauth_verify import oauth_verify_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(oauth_verify_bp)
    
    # Don't create tables on startup (do in init_production_db.py)
    # This saves memory
    
    return app


# Import User model and define user_loader AFTER create_app
# to avoid circular imports
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login - FIXED VERSION"""
    try:
        # Check if user_id is valid
        if not user_id or user_id == 'None' or user_id == 'none':
            print(f"⚠️  Warning: Invalid user_id received: {repr(user_id)}")
            return None
        
        # Convert to int
        user_id_int = int(user_id)
        
        # Load user
        user = User.query.get(user_id_int)
        
        if not user:
            print(f"⚠️  Warning: No user found with id: {user_id_int}")
        
        return user
        
    except (ValueError, TypeError) as e:
        print(f"❌ Error loading user with id '{user_id}': {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error loading user: {e}")
        return None