
from urllib.parse import urlencode
import secrets

client_id = '329204650680-0rmc3npi3a3kf1o3cocr4n56dd0so8o3.apps.googleusercontent.com'
redirect_uri = 'https://community-connect-project.onrender.com/auth/google/callback'
state = secrets.token_urlsafe(16)

params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid',
    'access_type': 'offline',
    'prompt': 'consent',
    'state': state
}

auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
print('🔗 TEST URL (copy and paste into browser):')
print(auth_url)
print()
print('This should take you to Google login page')
