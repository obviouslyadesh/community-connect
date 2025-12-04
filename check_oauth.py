# app/check_oauth.py - ENHANCED DEBUG VERSION
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
        """Exchange authorization code for tokens - WITH ENHANCED DEBUGGING"""
        print("\n" + "="*80)
        print("🔄 GOOGLE OAUTH TOKEN EXCHANGE DEBUG")
        print("="*80)
        
        # Get config
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        print(f"📝 Configuration Check:")
        print(f"   Client ID: {client_id}")
        print(f"   Client Secret: {'✅ SET' if client_secret else '❌ NOT SET OR EMPTY'}")
        print(f"   Redirect URI: {redirect_uri}")
        print(f"   Authorization Code: {code[:50]}...")
        
        if not all([client_id, client_secret, redirect_uri]):
            error_msg = f"Missing configuration - Client Secret: {'SET' if client_secret else 'NOT SET'}"
            print(f"❌ {error_msg}")
            raise Exception(f"Token exchange failed: {error_msg}")
        
        # Check if client_secret looks valid (should be about 40 chars)
        if client_secret and len(client_secret) < 20:
            print(f"⚠️  Warning: Client Secret looks too short ({len(client_secret)} chars)")
        
        # Token endpoint
        token_url = "https://oauth2.googleapis.com/token"
        
        # Prepare request with enhanced debugging
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        print(f"\n📤 Token Exchange Request:")
        print(f"   URL: {token_url}")
        print(f"   Client ID length: {len(client_id)} chars")
        print(f"   Client Secret length: {len(client_secret) if client_secret else 0} chars")
        print(f"   Redirect URI: {redirect_uri}")
        
        # Make request with timeout
        try:
            response = requests.post(token_url, data=data, timeout=10)
            print(f"\n📥 Response Status: {response.status_code}")
            
            # Try to parse response
            result = response.json()
            print(f"📥 Response Body: {result}")
            
            if response.status_code != 200:
                error = result.get('error', 'Unknown error')
                error_desc = result.get('error_description', 'No description')
                
                print(f"\n❌ Token Exchange Failed!")
                print(f"   Error: {error}")
                print(f"   Description: {error_desc}")
                
                # Common errors and solutions
                if error == 'invalid_client':
                    print(f"\n🔧 Solution: Client Secret is invalid or expired.")
                    print(f"   1. Regenerate Client Secret in Google Cloud Console")
                    print(f"   2. Update GOOGLE_CLIENT_SECRET in Render Environment")
                    print(f"   3. Wait 5-10 minutes for changes to propagate")
                elif error == 'invalid_grant':
                    print(f"\n🔧 Solution: Authorization code expired or already used.")
                    print(f"   Try logging in again.")
                elif error == 'redirect_uri_mismatch':
                    print(f"\n🔧 Solution: Redirect URI doesn't match.")
                    print(f"   Expected: {redirect_uri}")
                    print(f"   Check Google Cloud Console redirect URIs")
                
                raise Exception(f"Token exchange failed: {error} - {error_desc}")
            
            print("✅ Token exchange successful!")
            print(f"   Access Token: {result.get('access_token', '')[:30]}...")
            print(f"   Refresh Token: {'✅ Present' if 'refresh_token' in result else '❌ Missing'}")
            print("="*80)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Network Error: {e}")
            raise Exception(f"Network error during token exchange: {str(e)}")
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")
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