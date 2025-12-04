# deploy_verify.py - NEW FILE
import os
import sys

print("🚀 DEPLOYMENT VERIFICATION FOR RENDER")
print("="*70)

print("\n📋 Checking configuration files...")

# Check config.py
with open('config.py', 'r') as f:
    content = f.read()
    if 'community-connect-project.onrender.com' in content:
        print("✅ config.py has correct Render URL")
    else:
        print("❌ config.py needs URL update")

# Check render.yaml
with open('render.yaml', 'r') as f:
    content = f.read()
    if 'community-connect-project' in content:
        print("✅ render.yaml has correct service name")
    else:
        print("❌ render.yaml needs service name update")

print("\n🔧 Required Environment Variables for Render:")
print("""
1. SECRET_KEY (auto-generated)
2. DATABASE_URL (auto-generated)
3. GOOGLE_CLIENT_ID (YOU MUST SET THIS)
4. GOOGLE_CLIENT_SECRET (YOU MUST SET THIS)
5. GOOGLE_REDIRECT_URI (already in render.yaml)
""")

print("\n📍 Your Render URLs:")
print("   Application: https://community-connect-project.onrender.com")
print("   OAuth Callback: https://community-connect-project.onrender.com/auth/google/callback")

print("\n🔐 Google Cloud Console Setup:")
print("""
1. Go to: https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Add to Authorized JavaScript origins:
   - https://community-connect-project.onrender.com
4. Add to Authorized redirect URIs:
   - https://community-connect-project.onrender.com/auth/google/callback
5. Save and wait 5-10 minutes
""")

print("\n✅ After deployment, visit:")
print("   https://community-connect-project.onrender.com/verify-oauth")
print("   to verify your OAuth configuration")

print("\n" + "="*70)