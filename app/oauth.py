# app/oauth.py - FIXED VERSION
import requests
from flask import current_app
import secrets

class GoogleOAuth:
    @staticmethod
    def get_authorization_url():
        """Generate Google OAuth authorization URL - SIMPLIFIED"""
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16)
        
        # Use direct Google endpoints (no discovery needed)
        authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        
        # Get config - use correct variable names
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            raise ValueError("Missing Google OAuth configuration")
        
        # Build authorization URL
        from urllib.parse import urlencode
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        request_uri = f"{authorization_endpoint}?{urlencode(params)}"
        
        return request_uri, state
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for tokens - SIMPLIFIED"""
        # Get config
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError("Missing Google OAuth configuration")
        
        # Use direct token endpoint
        token_endpoint = "https://oauth2.googleapis.com/token"
        
        # Prepare token request
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # Request tokens
        token_response = requests.post(token_endpoint, data=token_data)
        token_json = token_response.json()
        
        if 'error' in token_json:
            error_msg = token_json.get('error_description', token_json['error'])
            raise Exception(f"Token exchange failed: {error_msg}")
        
        if token_response.status_code != 200:
            raise Exception(f"Token exchange failed with status {token_response.status_code}: {token_json}")
        
        return token_json
    
    @staticmethod
    def get_user_info(access_token):
        """Get user info using access token - SIMPLIFIED"""
        if not access_token:
            raise ValueError("No access token provided")
        
        # Use direct userinfo endpoint
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            error_msg = userinfo_response.text
            raise Exception(f"Failed to get user info (HTTP {userinfo_response.status_code}): {error_msg}")