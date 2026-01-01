import os
from dotenv import load_dotenv

# Load .env only if it exists
if os.path.exists('.env'):
    load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database - Docker/Production ready
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Fallback to SQLite only in development
        if os.environ.get('FLASK_ENV') == 'development':
            SQLALCHEMY_DATABASE_URI = 'sqlite:///community_connect.db'
        else:
            raise ValueError("DATABASE_URL environment variable is required")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # URLs - Smart detection
    @property
    def BASE_URL(self):
        if os.environ.get('RENDER'):
            return "https://community-connect-project.onrender.com"
        elif os.environ.get('DOCKER_ENV'):
            return os.environ.get('BASE_URL', 'http://localhost:10000')
        else:
            return os.environ.get('BASE_URL', 'http://localhost:5000')
    
    @property
    def GOOGLE_REDIRECT_URI(self):
        return f"{self.BASE_URL}/auth/google/callback"
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USERNAME)
    
    # API keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')