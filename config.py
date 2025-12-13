import os
from datetime import timedelta
from dotenv import load_dotenv

if os.environ.get('RENDER') is None:
    load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # URLs 
    if os.environ.get('RENDER'):
        # Production
        BASE_URL = "https://community-connect-project.onrender.com"
        GOOGLE_REDIRECT_URI = f"{BASE_URL}/auth/google/callback"
    else:
        # Development
        BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5001')
        GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', f'{BASE_URL}/auth/google/callback')
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USERNAME)
    
    # API keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')