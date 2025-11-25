import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - Render provides DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    
    # Fix for PostgreSQL (Render uses PostgreSQL)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-key')
    
    # Developer Mode - ALWAYS FALSE IN PRODUCTION
    DEVELOPER_MODE = False