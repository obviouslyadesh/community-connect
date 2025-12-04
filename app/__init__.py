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

# In app/__init__.py, update the create_app function:
def create_app(config_class='config.Config'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # DEBUG: Print Google OAuth configuration
    print("\n" + "="*60)
    print("🔥 GOOGLE OAUTH CONFIGURATION CHECK")
    print("="*60)
    
    client_id = app.config.get('GOOGLE_CLIENT_ID', 'NOT SET')
    print(f"GOOGLE_CLIENT_ID: {client_id}")
    
    if client_id and '329204650680' in client_id:
        print("✅ SUCCESS: Real Client ID loaded!")
    elif client_id and 'your-google-client-id' in client_id:
        print("❌ ERROR: Using placeholder Client ID!")
    else:
        print(f"⚠️  Client ID: {client_id}")
    
    redirect_uri = app.config.get('GOOGLE_REDIRECT_URI', 'NOT SET')
    print(f"Redirect URI: {redirect_uri}")
    
    # Check if on Render
    if os.environ.get('RENDER'):
        print("🚀 Running on RENDER")
        expected_uri = "https://community-connect-project.onrender.com/auth/google/callback"
        if redirect_uri != expected_uri:
            print(f"❌ WARNING: Redirect URI mismatch!")
            print(f"   Current: {redirect_uri}")
            print(f"   Expected: {expected_uri}")
    else:
        print("💻 Running locally")
    
    print("="*60 + "\n")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import and register blueprints
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    
    # Import oauth_verify blueprint
    from app.oauth_verify import oauth_verify_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(oauth_verify_bp)
    
    # Create database tables - WITH ERROR HANDLING
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️  Note: Database table creation error (tables may already exist): {e}")
            # Don't crash - tables likely already exist
    
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