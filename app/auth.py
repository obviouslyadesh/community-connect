from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.forms import LoginForm, RegistrationForm
from app.oauth import GoogleOAuth
import requests
import json
import secrets
from urllib.parse import urlencode

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Import User inside function
        from app.models import User
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Import User inside function
        from app.models import User
        
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/auth/google')
def google_login():
    """Initiate Google OAuth flow - WITH DEBUG LOGGING"""
    try:
        # Get current configuration
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        
        print("\n" + "="*60)
        print("🔍 DEBUG: Google OAuth Request")
        print("="*60)
        print(f"Client ID: {client_id}")
        print(f"Redirect URI: {redirect_uri}")
        
        # Verify configuration
        if not client_id:
            print("❌ ERROR: Client ID not configured")
            flash('OAuth configuration error. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        if not redirect_uri:
            print("❌ ERROR: Redirect URI not configured")
            print("   This usually means GOOGLE_REDIRECT_URI is not set in config")
            print("   On Render, check environment variables:")
            print("   - GOOGLE_CLIENT_ID")
            print("   - GOOGLE_CLIENT_SECRET")
            print("   - GOOGLE_REDIRECT_URI should be: https://community-connect-project.onrender.com/auth/google/callback")
            flash('OAuth configuration error. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if we're in production
        is_production = 'onrender.com' in redirect_uri
        
        print(f"Environment: {'Production' if is_production else 'Development'}")
        print("="*60)
        
        # Build the OAuth URL
        from urllib.parse import urlencode
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'email profile',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        print(f"\n✅ Generated URL: {auth_url[:100]}...")
        
        return redirect(auth_url)
        
    except Exception as e:
        print(f"❌ Google login error: {e}")
        import traceback
        traceback.print_exc()
        flash('Failed to connect to Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback - SIMPLIFIED"""
    # Get authorization code
    code = request.args.get('code')
    
    if not code:
        error = request.args.get('error')
        error_desc = request.args.get('error_description')
        print(f"❌ OAuth callback error: {error} - {error_desc}")
        flash(f'Authorization failed: {error_desc or "No code received"}', 'error')
        return redirect(url_for('auth.login'))
    
    print(f"✅ Received authorization code: {code[:30]}...")
    
    try:
        # Exchange code for tokens
        from app.oauth import GoogleOAuth
        from app.models import User
        
        print("🔄 Exchanging code for tokens...")
        tokens = GoogleOAuth.exchange_code_for_token(code)
        
        if not tokens or 'access_token' not in tokens:
            print(f"❌ Token exchange failed. Response: {tokens}")
            flash('Failed to get access token from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        access_token = tokens['access_token']
        print(f"✅ Got access token: {access_token[:30]}...")
        
        # Get user info
        print("🔄 Getting user info from Google...")
        user_info = GoogleOAuth.get_user_info(access_token)
        
        if not user_info:
            print("❌ Failed to get user info")
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        print(f"✅ User info received")
        
        # Get or create user
        user = User.get_or_create_google_user(user_info)
        
        if not user:
            print("❌ Failed to create/find user")
            flash('Failed to create user account.', 'error')
            return redirect(url_for('auth.login'))
        
        # Login the user
        login_user(user, remember=True)
        
        # Welcome message
        welcome_name = user_info.get('given_name') or user_info.get('name') or 'User'
        flash(f'Welcome, {welcome_name}!', 'success')
        
        print(f"✅ User logged in successfully: {user.email}")
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        print(f"❌ Google OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Failed to login with Google: {str(e)}', 'error')
        return redirect(url_for('auth.login'))