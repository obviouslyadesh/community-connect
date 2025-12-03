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
    
    # Google OAuth - NO DEFAULTS for production!
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Simple method for redirect URI (not a property)
    @staticmethod
    def get_google_redirect_uri():
        """Get the correct redirect URI based on environment"""
        if os.environ.get('RENDER'):
            # Production on Render
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                return f"{render_url}/auth/google/callback"
            render_service_name = os.environ.get('RENDER_SERVICE_NAME', 'community-connect-project')
            return f"https://{render_service_name}.onrender.com/auth/google/callback"
        else:
            # Local development
            return os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    # API Keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')
    
    def __init__(self):
        print("\n" + "="*60)
        print("📋 CONFIGURATION CHECK")
        print("="*60)
        
        # Environment detection
        if os.environ.get('RENDER'):
            print("✅ Environment: Production (Render)")
            print(f"   RENDER_EXTERNAL_URL: {os.environ.get('RENDER_EXTERNAL_URL', 'NOT SET')}")
        else:
            print("✅ Environment: Development (Local)")
        
        # Check Google OAuth config
        print(f"\n🔑 Google OAuth Configuration:")
        print(f"   Client ID: {self.GOOGLE_CLIENT_ID[:40]}..." if self.GOOGLE_CLIENT_ID else "❌ Client ID: NOT SET")
        print(f"   Client Secret: {'✅ SET' if self.GOOGLE_CLIENT_SECRET else '❌ NOT SET'}")
        print(f"   Redirect URI: {self.get_google_redirect_uri()}")
        
        # Critical check for production
        if os.environ.get('RENDER'):
            if not self.GOOGLE_CLIENT_ID:
                print("\n❌ CRITICAL ERROR: GOOGLE_CLIENT_ID not set in Render environment variables!")
            if not self.GOOGLE_CLIENT_SECRET:
                print("❌ CRITICAL ERROR: GOOGLE_CLIENT_SECRET not set in Render environment variables!")
        
        print("="*60 + "\n")