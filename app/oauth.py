import requests
from flask import current_app
import secrets

class GoogleOAuth:
    @staticmethod
    def get_authorization_url():
        state = secrets.token_urlsafe(16)
        
        authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            raise ValueError("Missing Google OAuth configuration")
        
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
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            raise ValueError("Missing Google OAuth configuration")
        
        token_endpoint = "https://oauth2.googleapis.com/token"
        
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_endpoint, data=token_data)
        token_json = token_response.json()
        
        if 'error' in token_json:
            error_msg = token_json.get('error_description', token_json['error'])
            raise Exception(f"Token exchange failed: {error_msg}")
        
        if token_response.status_code != 200:
            raise Exception(f"Token exchange failed with status {token_response.status_code}")
        
        return token_json
    
    @staticmethod
    def get_user_info(access_token):
        if not access_token:
            raise ValueError("No access token provided")
        
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            raise Exception(f"Failed to get user info")