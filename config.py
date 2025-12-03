# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# LOAD .env FILE
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-local-development-secret-key'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///community_connect.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY') or 'demo-weather-key'
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY') or 'demo-maps-key'
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # OAuth Settings
    OAUTH_REDIRECT_URI = 'http://localhost:5001/auth/google/callback'
    GOOGLE_REDIRECT_URI = OAUTH_REDIRECT_URI
    
    def __init__(self):
        print("\n" + "="*60)
        print("📋 CONFIGURATION LOADED")
        print("="*60)
        print(f"Database: {self.SQLALCHEMY_DATABASE_URI}")
        
        if not self.GOOGLE_CLIENT_ID:
            print("❌ ERROR: GOOGLE_CLIENT_ID is not set!")
            print("   Check your .env file")
        elif 'your-google-client-id' in str(self.GOOGLE_CLIENT_ID):
            print("❌ WARNING: Using placeholder GOOGLE_CLIENT_ID!")
            print(f"   Current value: {self.GOOGLE_CLIENT_ID}")
        elif '329204650680' in str(self.GOOGLE_CLIENT_ID):
            print(f"✅ SUCCESS: Real Client ID loaded: {self.GOOGLE_CLIENT_ID[:40]}...")
        else:
            print(f"ℹ️  GOOGLE_CLIENT_ID: {self.GOOGLE_CLIENT_ID[:50]}...")
        
        print("="*60 + "\n")