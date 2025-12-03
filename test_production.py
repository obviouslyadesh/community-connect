# test_production.py
import os

print("🧪 TESTING PRODUCTION CONFIGURATION")
print("="*60)

# Simulate Render environment
os.environ['RENDER'] = 'true'
os.environ['RENDER_EXTERNAL_URL'] = 'https://community-connect-project.onrender.com'

# Load config
from config import Config
config = Config()

print("\n📋 For Google Cloud Console, configure:")
print("="*60)
print("1. Authorized JavaScript origins:")
print(f"   https://community-connect-project.onrender.com")
print("\n2. Authorized redirect URIs:")
print(f"   {config.GOOGLE_REDIRECT_URI}")
print("   http://localhost:5001/auth/google/callback")
print("   http://127.0.0.1:5001/auth/google/callback")
print("\n3. OAuth Consent Screen:")
print("   - Must be PUBLISHED (not in Testing mode)")
print("   - Add your email as Test User if in Testing mode")
print("="*60)