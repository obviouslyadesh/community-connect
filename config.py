# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env only in development
if os.environ.get('RENDER') is None:
    load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth - REQUIRED, no defaults
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Redirect URI - EXACT strings
    if os.environ.get('RENDER'):
        # Production - EXACT string
        GOOGLE_REDIRECT_URI = "https://community-connect-project.onrender.com/auth/google/callback"
    else:
        # Development
        GOOGLE_REDIRECT_URI = "http://localhost:5001/auth/google/callback"
    
    # Optional API keys
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo-weather-key')
    MAPS_API_KEY = os.environ.get('MAPS_API_KEY', 'demo-maps-key')
    
    def __init__(self):
        print("\n" + "="*60)
        print("🔥 GOOGLE OAUTH CONFIGURATION")
        print("="*60)
        
        env = "Production" if os.environ.get('RENDER') else "Development"
        print(f"Environment: {env}")
        
        print(f"\n🔑 Google OAuth Credentials:")
        print(f"Client ID: {self.GOOGLE_CLIENT_ID[:40]}..." if self.GOOGLE_CLIENT_ID else "❌ Client ID: NOT SET")
        print(f"Client Secret: {'✅ SET' if self.GOOGLE_CLIENT_SECRET else '❌ NOT SET'}")
        print(f"Redirect URI: {self.GOOGLE_REDIRECT_URI}")
        
        # Critical checks
        if os.environ.get('RENDER'):
            if not self.GOOGLE_CLIENT_ID:
                print("\n❌ CRITICAL: GOOGLE_CLIENT_ID missing on Render!")
            if not self.GOOGLE_CLIENT_SECRET:
                print("❌ CRITICAL: GOOGLE_CLIENT_SECRET missing on Render!")
        
        print("="*60 + "\n")