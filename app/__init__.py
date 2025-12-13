from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config_class)
    
    # PostgreSQL URL
    if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
            'postgres://', 'postgresql://', 1
        )
    
    # Initialize with minimal settings
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import blueprints only when needed
    from app.auth import auth as auth_bp
    from app.routes import main as main_bp
    from app.oauth_verify import oauth_verify_bp
        
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(oauth_verify_bp)
    
    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    try:
        if not user_id or user_id == 'None' or user_id == 'none':
            return None
        
        user_id_int = int(user_id)
        user = User.query.get(user_id_int)
        return user
        
    except (ValueError, TypeError):
        return None
    except Exception:
        return None