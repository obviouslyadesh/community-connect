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
    
    def __init__(self):
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT CONFIGURATION")
        print("="*60)
        
        env = "🚀 PRODUCTION (Render)" if os.environ.get('RENDER') else "💻 DEVELOPMENT"
        print(f"Environment: {env}")
        print(f"Base URL: {self.BASE_URL}")
        
        print(f"\n🔑 Google OAuth:")
        print(f"Client ID: {'✅ SET' if self.GOOGLE_CLIENT_ID else '❌ NOT SET'}")
        print(f"Client Secret: {'✅ SET' if self.GOOGLE_CLIENT_SECRET else '❌ NOT SET'}")
        print(f"Redirect URI: {self.GOOGLE_REDIRECT_URI}")
        
        print(f"\n📧 Email Configuration:")
        print(f"SMTP Server: {self.SMTP_SERVER}")
        print(f"From Email: {self.FROM_EMAIL}")
        
        # Email provider recommendation
        if os.environ.get('RENDER'):
            if not self.SMTP_USERNAME or not self.SMTP_PASSWORD:
                print("⚠️  Email not configured. For production, consider:")
                print("   1. SendGrid (100 emails/day free)")
                print("   2. Resend (100 emails/month free)")
                print("   3. Or continue with Gmail (500 emails/day)")
            else:
                print("✅ Email credentials set")
        
        # Critical production checks
        if os.environ.get('RENDER'):
            missing = []
            if not self.GOOGLE_CLIENT_ID:
                missing.append('GOOGLE_CLIENT_ID')
            if not self.GOOGLE_CLIENT_SECRET:
                missing.append('GOOGLE_CLIENT_SECRET')
            if not self.SECRET_KEY or self.SECRET_KEY == 'dev-secret-key-change-in-production':
                missing.append('SECRET_KEY (should be a strong random string)')
            
            if missing:
                print(f"\n❌ MISSING CRITICAL CONFIGURATION: {', '.join(missing)}")
                print("   Set these in Render Dashboard → Environment")
            else:
                print("\n✅ All critical configurations are set!")
        
        print("="*60 + "\n")