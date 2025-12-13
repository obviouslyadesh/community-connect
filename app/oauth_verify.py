from flask import Blueprint, current_app, request, render_template
import os

oauth_verify_bp = Blueprint('oauth_verify', __name__)

@oauth_verify_bp.route('/verify-oauth')
def verify_oauth():
    config = current_app.config
    
    is_production = os.environ.get('RENDER') is not None
    base_url = request.host_url.rstrip('/')
    
    google_config = {
        'GOOGLE_CLIENT_ID': config.get('GOOGLE_CLIENT_ID', '❌ NOT SET'),
        'GOOGLE_CLIENT_SECRET': '✅ SET' if config.get('GOOGLE_CLIENT_SECRET') else '❌ NOT SET',
        'GOOGLE_REDIRECT_URI': config.get('GOOGLE_REDIRECT_URI', '❌ NOT SET'),
    }
    
    expected_config = {
        'expected_redirect_uri': 'https://community-connect-project.onrender.com/auth/google/callback' if is_production else 'http://localhost:5001/auth/google/callback',
    }
    
    redirect_matches = google_config['GOOGLE_REDIRECT_URI'] == expected_config['expected_redirect_uri']
    
    missing_config = []
    if not google_config['GOOGLE_CLIENT_ID'] or google_config['GOOGLE_CLIENT_ID'] == '❌ NOT SET':
        missing_config.append('GOOGLE_CLIENT_ID')
    
    if not config.get('GOOGLE_CLIENT_SECRET'):
        missing_config.append('GOOGLE_CLIENT_SECRET')
    
    return render_template('oauth_verify.html',
        is_production=is_production,
        base_url=base_url,
        google_config=google_config,
        expected_config=expected_config,
        redirect_matches=redirect_matches,
        missing_config=missing_config
    )