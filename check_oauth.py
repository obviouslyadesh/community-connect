import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

with app.app_context():
    print("🔍 OAuth Configuration Check:")
    print("=" * 50)
    
    config = app.config
    
    # Check Client ID
    client_id = config.get('GOOGLE_CLIENT_ID')
    print(f"✅ Client ID: {'Set' if client_id else '❌ NOT SET'}")
    if client_id:
        print(f"   Value: {client_id[:30]}...")
        print(f"   Correct format: {'.apps.googleusercontent.com' in client_id}")
    
    # Check Client Secret
    client_secret = config.get('GOOGLE_CLIENT_SECRET')
    print(f"\n✅ Client Secret: {'Set' if client_secret else '❌ NOT SET'}")
    if client_secret:
        print(f"   Length: {len(client_secret)} characters")
    
    # Check Redirect URI
    redirect_uri = config.get('OAUTH_REDIRECT_URI')
    print(f"\n✅ Redirect URI: {redirect_uri}")
    print(f"   Expected: http://localhost:5001/auth/google/callback")
    print(f"   Matches: {redirect_uri == 'http://localhost:5001/auth/google/callback'}")
    
    print("\n" + "=" * 50)
    print("📋 Troubleshooting Checklist:")
    print("1. Go to Google Cloud Console")
    print("2. Check OAuth consent screen is configured (External)")
    print("3. Verify redirect URI matches exactly")
    print("4. Check Client ID ends with .apps.googleusercontent.com")
    print("5. Ensure Google People API is enabled")