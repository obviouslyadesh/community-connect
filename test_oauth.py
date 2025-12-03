# test_oauth_url.py
import os
from urllib.parse import urlencode

# Your credentials
CLIENT_ID = "329204650680-0rmc3npi3a3kf1o3cocr4n56dd0so8o3.apps.googleusercontent.com"
REDIRECT_URI = "https://community-connect-project.onrender.com/auth/google/callback"

print("🧪 TESTING GOOGLE OAUTH URL GENERATION")
print("="*60)

# Test different scope formats
scopes = [
    # Option 1: Space-separated keywords (might not work)
    "email profile",
    
    # Option 2: Full URL scopes (RECOMMENDED)
    "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
    
    # Option 3: With openid
    "openid email profile",
    
    # Option 4: Just email
    "https://www.googleapis.com/auth/userinfo.email",
]

for i, scope in enumerate(scopes, 1):
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': scope,
        'access_type': 'offline',
        'prompt': 'consent',
        'state': 'test123'  # Add state parameter
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    print(f"\n🔗 Option {i}: Scope = '{scope}'")
    print(f"URL: {auth_url[:100]}...")
    print(f"Length: {len(auth_url)} chars")
    
    # Test if URL looks valid
    if 'openid' in scope or 'https://www.googleapis.com' in scope:
        print("✅ Using recommended scope format")
    else:
        print("⚠️  Using simple scope format (might cause 400)")

print("\n" + "="*60)
print("📋 Most likely issue: Scope format")
print("Try using FULL URL scopes instead of keywords")
print("="*60)