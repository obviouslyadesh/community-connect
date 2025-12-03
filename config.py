# config.py - SIMPLIFIED VERSION
import os
from datetime import timedelta
from dotenv import load_dotenv

# Only load .env in development
if os.environ.get('RENDER') is None and os.environ.get('FLASK_ENV') != 'production':
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth - NO DEFAULTS!
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # DIRECT ATTRIBUTE - NOT A PROPERTY
    if os.environ.get('RENDER'):
        # Production on Render
        render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://community-connect-project.onrender.com')
        GOOGLE_REDIRECT_URI = f"{render_url}/auth/google/callback"
    else:
        # Local development
        GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')
    
    def __init__(self):
        print("\n" + "="*60)
        print("📋 CONFIGURATION CHECK - PRODUCTION")
        print("="*60)
        
        if os.environ.get('RENDER'):
            print("✅ Environment: Production (Render)")
            print(f"   RENDER_EXTERNAL_URL: {os.environ.get('RENDER_EXTERNAL_URL', 'NOT SET')}")
        else:
            print("✅ Environment: Development (Local)")
        
        print(f"\n🔑 Google OAuth:")
        print(f"   Client ID: {self.GOOGLE_CLIENT_ID[:40]}..." if self.GOOGLE_CLIENT_ID else "❌ Client ID: NOT SET")
        print(f"   Client Secret: {'✅ SET' if self.GOOGLE_CLIENT_SECRET else '❌ NOT SET'}")
        print(f"   Redirect URI: {self.GOOGLE_REDIRECT_URI}")
        
        if os.environ.get('RENDER'):
            if not self.GOOGLE_CLIENT_ID:
                print("\n❌ CRITICAL: GOOGLE_CLIENT_ID missing from Render environment!")
            if not self.GOOGLE_CLIENT_SECRET:
                print("❌ CRITICAL: GOOGLE_CLIENT_SECRET missing from Render environment!")
            if not self.GOOGLE_REDIRECT_URI:
                print("❌ CRITICAL: GOOGLE_REDIRECT_URI not calculated!")
        
        print("="*60 + "\n")