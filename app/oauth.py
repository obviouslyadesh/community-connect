import requests
from flask import current_app
import secrets

class GoogleOAuth:
    @staticmethod
    def get_google_provider_cfg():
        """Get Google's OAuth 2.0 configuration"""
        return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    
    @staticmethod
    def get_authorization_url():
        """Generate Google OAuth authorization URL"""
        google_provider_cfg = GoogleOAuth.get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16)
        
        # Build authorization URL
        request_uri = (
            f"{authorization_endpoint}"
            f"?response_type=code"
            f"&client_id={current_app.config['GOOGLE_CLIENT_ID']}"
            f"&redirect_uri={current_app.config['OAUTH_REDIRECT_URI']}"
            f"&scope=openid%20email%20profile"
            f"&state={state}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        
        return request_uri, state
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for tokens"""
        google_provider_cfg = GoogleOAuth.get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Prepare token request
        token_data = {
            'code': code,
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': current_app.config['OAUTH_REDIRECT_URI'],
            'grant_type': 'authorization_code'
        }
        
        # Request tokens
        token_response = requests.post(token_endpoint, data=token_data)
        token_json = token_response.json()
        
        if 'error' in token_json:
            raise Exception(f"Token exchange failed: {token_json}")
        
        return token_json
    
    @staticmethod
    def get_user_info(access_token):
        """Get user info using access token"""
        google_provider_cfg = GoogleOAuth.get_google_provider_cfg()
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            raise Exception(f"Failed to get user info: {userinfo_response.text}")