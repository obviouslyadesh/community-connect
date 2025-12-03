# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions (without app context first)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import User model for the user_loader (import here to avoid circular imports)
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

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
        print("✅ SUCCESS: Real Client ID loaded from .env!")
    elif client_id and 'your-google-client-id' in client_id:
        print("❌ ERROR: Still using placeholder Client ID!")
        print("   Make sure .env file has correct values")
    else:
        print(f"⚠️  Client ID: {client_id}")
    
    redirect_uri = app.config.get('GOOGLE_REDIRECT_URI', app.config.get('OAUTH_REDIRECT_URI', 'NOT SET'))
    print(f"Redirect URI: {redirect_uri}")
    print("="*60 + "\n")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import and register blueprints (inside function to avoid circular imports)
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app