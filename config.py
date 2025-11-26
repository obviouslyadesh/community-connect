import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    
    # Fix for Render's PostgreSQL URL format
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-key')
    
    # Developer Mode - ALWAYS FALSE IN PRODUCTION
    DEVELOPER_MODE = os.environ.get('DEVELOPER_MODE', 'false').lower() == 'true'