# app/oauth_verify.py - NEW FILE
from flask import Blueprint, jsonify, current_app, request, render_template
import requests
import os
import urllib.parse

oauth_verify_bp = Blueprint('oauth_verify', __name__)

@oauth_verify_bp.route('/verify-oauth')
def verify_oauth():
    """Endpoint to verify OAuth configuration"""
    config = current_app.config
    
    # Get environment info
    is_production = os.environ.get('RENDER') is not None
    base_url = request.host_url.rstrip('/')
    
    # Google OAuth config
    google_config = {
        'GOOGLE_CLIENT_ID': config.get('GOOGLE_CLIENT_ID', '❌ NOT SET'),
        'GOOGLE_CLIENT_SECRET': '✅ SET' if config.get('GOOGLE_CLIENT_SECRET') else '❌ NOT SET',
        'GOOGLE_REDIRECT_URI': config.get('GOOGLE_REDIRECT_URI', '❌ NOT SET'),
    }
    
    # Expected values
    expected_config = {
        'production_url': 'https://community-connect-project.onrender.com',
        'expected_redirect_uri': 'https://community-connect-project.onrender.com/auth/google/callback' if is_production else 'http://localhost:5001/auth/google/callback',
        'google_cloud_console_url': 'https://console.cloud.google.com/apis/credentials'
    }
    
    # Check if redirect URI matches
    redirect_matches = google_config['GOOGLE_REDIRECT_URI'] == expected_config['expected_redirect_uri']
    
    # Test connectivity
    connectivity = {}
    try:
        # Try to reach Google's OAuth discovery endpoint
        response = requests.get('https://accounts.google.com/.well-known/openid-configuration', timeout=5)
        connectivity['google_oauth_endpoint'] = {
            'status': '✅ Reachable' if response.status_code == 200 else f'❌ Error: {response.status_code}',
            'status_code': response.status_code
        }
    except Exception as e:
        connectivity['google_oauth_endpoint'] = {
            'status': f'❌ Error: {str(e)}',
            'status_code': None
        }
    
    # Check if all required config is present
    missing_config = []
    recommendations = []
    
    if not google_config['GOOGLE_CLIENT_ID'] or google_config['GOOGLE_CLIENT_ID'] == '❌ NOT SET':
        missing_config.append('GOOGLE_CLIENT_ID')
        recommendations.append('Set GOOGLE_CLIENT_ID in Render Dashboard → Environment')
    
    if not config.get('GOOGLE_CLIENT_SECRET'):
        missing_config.append('GOOGLE_CLIENT_SECRET')
        recommendations.append('Set GOOGLE_CLIENT_SECRET in Render Dashboard → Environment')
    
    if not redirect_matches:
        recommendations.append(f'Update Google Cloud Console redirect URI to: {expected_config["expected_redirect_uri"]}')
        recommendations.append(f'Current redirect URI: {google_config["GOOGLE_REDIRECT_URI"]}')
    
    # Generate test auth URL if possible
    test_auth_url = None
    if config.get('GOOGLE_CLIENT_ID') and config.get('GOOGLE_REDIRECT_URI'):
        try:
            params = {
                'client_id': config.get('GOOGLE_CLIENT_ID'),
                'redirect_uri': config.get('GOOGLE_REDIRECT_URI'),
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline',
                'prompt': 'consent'
            }
            test_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        except:
            pass
    
    return render_template('oauth_verify.html',
        is_production=is_production,
        base_url=base_url,
        google_config=google_config,
        expected_config=expected_config,
        redirect_matches=redirect_matches,
        connectivity=connectivity,
        missing_config=missing_config,
        recommendations=recommendations,
        test_auth_url=test_auth_url
    )

# Create HTML template
def create_verify_template():
    """Create the verification template"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    template_content = """<!DOCTYPE html>
<html>
<head>
    <title>OAuth Configuration Verification</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section { margin-bottom: 30px; }
        h1 { color: #333; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 25px; }
        .status { padding: 8px 15px; border-radius: 5px; font-weight: bold; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .warning { background: #fff3cd; color: #856404; }
        .info { background: #d1ecf1; color: #0c5460; }
        .config-item { margin: 15px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #4285f4; }
        .config-label { font-weight: bold; color: #333; }
        .config-value { color: #666; word-break: break-all; }
        .recommendation { padding: 10px 15px; margin: 10px 0; background: #e3f2fd; border-left: 4px solid #2196f3; }
        .button { background: #4285f4; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .button:hover { background: #357ae8; }
        .button-secondary { background: #6c757d; }
        .button-secondary:hover { background: #5a6268; }
        .test-section { background: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .url-display { background: #f8f9fa; padding: 10px; border: 1px solid #dee2e6; border-radius: 5px; font-family: monospace; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🔍 Google OAuth Configuration Verification</h1>
            
            <div class="section">
                <div class="status {{ 'success' if not missing_config else 'error' }}">
                    {% if not missing_config %}
                    ✅ All required configurations are set
                    {% else %}
                    ❌ Missing configurations: {{ missing_config|join(', ') }}
                    {% endif %}
                </div>
                
                <div class="status {{ 'success' if redirect_matches else 'warning' }}">
                    {% if redirect_matches %}
                    ✅ Redirect URI matches expected value
                    {% else %}
                    ⚠️ Redirect URI does not match expected value
                    {% endif %}
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Environment Information</h2>
                <div class="config-item">
                    <div class="config-label">Environment</div>
                    <div class="config-value">
                        {% if is_production %}
                        🚀 Production (Render)
                        {% else %}
                        💻 Development
                        {% endif %}
                    </div>
                </div>
                <div class="config-item">
                    <div class="config-label">Current Application URL</div>
                    <div class="config-value">{{ base_url }}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔑 Google OAuth Configuration</h2>
                {% for key, value in google_config.items() %}
                <div class="config-item">
                    <div class="config-label">{{ key }}</div>
                    <div class="config-value">{{ value }}</div>
                </div>
                {% endfor %}
                
                <div class="config-item">
                    <div class="config-label">Expected Redirect URI ({{ 'Production' if is_production else 'Development' }})</div>
                    <div class="config-value">{{ expected_config.expected_redirect_uri }}</div>
                </div>
            </div>
            
            {% if connectivity %}
            <div class="section">
                <h2>🌐 Connectivity Tests</h2>
                {% for service, info in connectivity.items() %}
                <div class="config-item">
                    <div class="config-label">{{ service|replace('_', ' ')|title }}</div>
                    <div class="config-value">{{ info.status }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if recommendations %}
            <div class="section">
                <h2>🚨 Action Required</h2>
                {% for rec in recommendations %}
                <div class="recommendation">{{ loop.index }}. {{ rec }}</div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="test-section">
                <h2>🧪 Test OAuth Login</h2>
                {% if test_auth_url %}
                <p>Click the button below to test Google OAuth login:</p>
                <a href="{{ test_auth_url }}" class="button" target="_blank">Test Google Login</a>
                <p>Or use this URL:</p>
                <div class="url-display">{{ test_auth_url }}</div>
                {% else %}
                <p>Cannot generate test URL. Please fix the configuration issues above first.</p>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>📝 Setup Instructions</h2>
                <ol>
                    <li>Go to <a href="https://console.cloud.google.com/apis/credentials" target="_blank">Google Cloud Console → Credentials</a></li>
                    <li>Select your OAuth 2.0 Client ID</li>
                    <li>Add to <strong>Authorized JavaScript origins</strong>:
                        <div class="url-display">https://community-connect-project.onrender.com</div>
                    </li>
                    <li>Add to <strong>Authorized redirect URIs</strong>:
                        <div class="url-display">https://community-connect-project.onrender.com/auth/google/callback</div>
                    </li>
                    <li>Save changes</li>
                    <li>Wait 5-10 minutes for changes to propagate</li>
                </ol>
            </div>
            
            <div style="margin-top: 30px; text-align: center;">
                <a href="/" class="button button-secondary">← Back to Home</a>
                <a href="https://render.com" class="button button-secondary" target="_blank">Render Dashboard</a>
                <a href="https://console.cloud.google.com" class="button button-secondary" target="_blank">Google Cloud Console</a>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    template_path = os.path.join(template_dir, 'oauth_verify.html')
    with open(template_path, 'w') as f:
        f.write(template_content)
    print(f"✅ Created verification template at: {template_path}")

# Call this when the blueprint is initialized
create_verify_template()

@oauth_verify_bp.route('/debug-client-secret')
def debug_client_secret():
    """Debug endpoint to check client secret (BE CAREFUL WITH THIS)"""
    config = current_app.config
    client_secret = config.get('GOOGLE_CLIENT_SECRET', 'NOT SET')
    
    return f"""
    <html>
        <head><title>Client Secret Debug</title></head>
        <body>
            <h1>Client Secret Debug</h1>
            <p><strong>Is Set:</strong> {'✅ YES' if client_secret and client_secret != 'NOT SET' else '❌ NO'}</p>
            <p><strong>Length:</strong> {len(client_secret) if client_secret and client_secret != 'NOT SET' else 0}</p>
            <p><strong>First 5 chars:</strong> {client_secret[:5] if client_secret and client_secret != 'NOT SET' else 'N/A'}</p>
            <p><strong>Last 5 chars:</strong> {client_secret[-5:] if client_secret and client_secret != 'NOT SET' else 'N/A'}</p>
            <hr>
            <h3>Common Issues:</h3>
            <ol>
                <li>Copy the secret WITHOUT quotes</li>
                <li>No spaces at beginning or end</li>
                <li>Click "Save Changes" on Render</li>
                <li>Wait 2 minutes after saving</li>
            </ol>
            <a href="/verify-oauth">← Back to Verification</a>
        </body>
    </html>
    """