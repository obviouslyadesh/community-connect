# config.py
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
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Determine environment and set redirect URI
    @property
    def GOOGLE_REDIRECT_URI(self):
        # Production on Render
        if os.environ.get('RENDER'):
            render_service_name = os.environ.get('RENDER_SERVICE_NAME', 'community-connect')
            return f"https://{render_service_name}.onrender.com/auth/google/callback"
        # Local development
        else:
            return os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')
    
    def __init__(self):
        print("\n" + "="*60)
        print("📋 CONFIGURATION CHECK - FIXING invalid_client ERROR")
        print("="*60)
        
        # Environment detection
        if os.environ.get('RENDER'):
            print("✅ Environment: Production (Render)")
            print(f"   RENDER_EXTERNAL_URL: {os.environ.get('RENDER_EXTERNAL_URL', 'NOT SET')}")
            print(f"   RENDER_SERVICE_NAME: {os.environ.get('RENDER_SERVICE_NAME', 'NOT SET')}")
        else:
            print("✅ Environment: Development (Local)")
        
        # Check Google OAuth config
        print(f"\n🔑 Google OAuth Configuration:")
        print(f"   Client ID: {self.GOOGLE_CLIENT_ID[:40]}..." if self.GOOGLE_CLIENT_ID else "❌ Client ID: NOT SET")
        print(f"   Client Secret: {'✅ SET' if self.GOOGLE_CLIENT_SECRET else '❌ NOT SET'}")
        print(f"   Redirect URI: {self.GOOGLE_REDIRECT_URI}")
        
        # Critical check for production
        if os.environ.get('RENDER'):
            if not self.GOOGLE_CLIENT_ID:
                print("\n❌ CRITICAL ERROR: GOOGLE_CLIENT_ID not set in Render environment variables!")
            if not self.GOOGLE_CLIENT_SECRET:
                print("❌ CRITICAL ERROR: GOOGLE_CLIENT_SECRET not set in Render environment variables!")
            
            # Verify redirect URI format
            if 'onrender.com' not in self.GOOGLE_REDIRECT_URI:
                print(f"❌ WRONG Redirect URI for production: {self.GOOGLE_REDIRECT_URI}")
                print("   Should be: https://your-app-name.onrender.com/auth/google/callback")
        
        print("="*60 + "\n")