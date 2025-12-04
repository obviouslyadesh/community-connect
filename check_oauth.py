# app/oauth.py - SIMPLIFIED VERSION
import requests
from flask import current_app
import secrets
from urllib.parse import urlencode

class GoogleOAuth:
    @staticmethod
    def get_authorization_url():
        """Generate Google OAuth authorization URL"""
        # Get config
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            raise ValueError("Missing Google OAuth configuration")
        
        # Generate state
        state = secrets.token_urlsafe(16)
        
        # Build URL
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return auth_url, state
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for tokens"""
        print("\n" + "="*60)
        print("🔄 TOKEN EXCHANGE")
        print("="*60)
        
        # Get config
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        print(f"Client ID: {client_id[:30]}...")
        print(f"Client Secret: {'*' * 10}{client_secret[-4:] if client_secret else 'NOT SET'}")
        print(f"Redirect URI: {redirect_uri}")
        print(f"Code: {code[:30]}...")
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError("Missing Google OAuth configuration")
        
        # Token endpoint
        token_url = "https://oauth2.googleapis.com/token"
        
        # Prepare request
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # Make request
        response = requests.post(token_url, data=data)
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"📡 Response: {result}")
            
            if response.status_code != 200:
                error = result.get('error', 'Unknown error')
                error_desc = result.get('error_description', 'No description')
                raise Exception(f"Token exchange failed: {error} - {error_desc}")
            
            print("✅ Token exchange successful!")
            print("="*60)
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
    
    @staticmethod
    def get_user_info(access_token):
        """Get user info from Google"""
        if not access_token:
            raise ValueError("No access token")
        
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(userinfo_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user info: {response.status_code} - {response.text}")