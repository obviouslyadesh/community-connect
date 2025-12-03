# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Only load .env in development
if os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('RENDER'):
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database - Render provides DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///community_connect.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth - REQUIRED in production
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Redirect URI - different for production
    if os.environ.get('RENDER'):
        # Production on Render
        GOOGLE_REDIRECT_URI = f"https://{os.environ.get('RENDER_SERVICE_NAME', 'your-app')}.onrender.com/auth/google/callback"
    else:
        # Local development
        GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    def __init__(self):
        print("\n" + "="*60)
        print("📋 CONFIGURATION")
        print("="*60)
        print(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")
        print(f"Database: {self.SQLALCHEMY_DATABASE_URI[:50]}...")
        
        if not self.GOOGLE_CLIENT_ID:
            print("❌ ERROR: GOOGLE_CLIENT_ID is not set!")
        elif 'your-google-client-id' in str(self.GOOGLE_CLIENT_ID):
            print("❌ ERROR: Using placeholder GOOGLE_CLIENT_ID!")
        else:
            print(f"✅ GOOGLE_CLIENT_ID: {self.GOOGLE_CLIENT_ID[:40]}...")
        
        print(f"Redirect URI: {self.GOOGLE_REDIRECT_URI}")
        print("="*60 + "\n")