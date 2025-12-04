# app/auth.py - COMPLETE FIXED VERSION
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
    """Initiate Google OAuth flow"""
    try:
        from app.oauth import GoogleOAuth
        import secrets
        
        # Get config
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            flash('OAuth not configured. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Generate state
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        
        # Build URL manually (or use GoogleOAuth.get_authorization_url())
        from urllib.parse import urlencode
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
        
        print(f"\n✅ Google OAuth URL:")
        print(f"{auth_url}")
        
        return redirect(auth_url)
        
    except Exception as e:
        print(f"❌ Google login error: {e}")
        flash('Failed to connect to Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
@auth.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback - FIXED VERSION"""
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
        
        print(f"✅ User info received: {user_info.get('email')}")
        
        # Get or create user
        print("🔄 Getting or creating user...")
        user = User.get_or_create_google_user(user_info)
        
        if not user:
            print("❌ Failed to create/find user")
            flash('Failed to create user account.', 'error')
            return redirect(url_for('auth.login'))
        
        # CRITICAL: Ensure user has an ID before logging in
        if user.id is None:
            print("🔄 User has no ID, committing to database...")
            db.session.add(user)
            db.session.commit()
            print(f"✅ User committed to database with ID: {user.id}")
        
        # Debug: Print user info
        print(f"📋 User details before login:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Google ID: {user.google_id}")
        
        # Login the user - IMPORTANT FIX: Use remember=False initially
        login_result = login_user(user, remember=False)
        
        if not login_result:
            print("❌ login_user() returned False!")
            flash('Login failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Store user info in session for debugging
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        # Welcome message
        welcome_name = user_info.get('given_name') or user_info.get('name') or user.username
        flash(f'Welcome, {welcome_name}!', 'success')
        
        print(f"✅ User logged in successfully: {user.email}")
        print(f"   User ID in session: {session.get('user_id')}")
        print(f"   Current user authenticated: {current_user.is_authenticated}")
        
        # Redirect to dashboard
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        print(f"❌ Google OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Failed to login with Google: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

# Add debug routes for troubleshooting
@auth.route('/debug/session')
def debug_session():
    """Debug session information"""
    session_info = {
        'session_id': session.get('_id'),
        'user_id': session.get('user_id'),
        'user_email': session.get('user_email'),
        'oauth_state': session.get('oauth_state'),
        '_fresh': session.get('_fresh'),
        '_user_id': session.get('_user_id'),  # Flask-Login's user ID
    }
    
    return f"""
    <html>
        <head><title>Session Debug</title></head>
        <body>
            <h1>Session Debug</h1>
            <pre>{json.dumps(session_info, indent=2)}</pre>
            <h2>Current User:</h2>
            <pre>{json.dumps({
                'is_authenticated': current_user.is_authenticated,
                'id': getattr(current_user, 'id', 'No id attribute'),
                'username': getattr(current_user, 'username', 'No username'),
                'email': getattr(current_user, 'email', 'No email')
            }, indent=2)}</pre>
            <hr>
            <a href="/">Home</a> | 
            <a href="/auth/google">Test Google Login</a> | 
            <a href="/logout">Logout</a>
        </body>
    </html>
    """

@auth.route('/debug/users')
def debug_users():
    """Debug all users in database"""
    from app.models import User
    users = User.query.all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'google_id': user.google_id,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return f"""
    <html>
        <head><title>Users Debug</title></head>
        <body>
            <h1>Users in Database</h1>
            <pre>{json.dumps(user_list, indent=2)}</pre>
            <hr>
            <a href="/">Home</a> | 
            <a href="/debug/session">Session Debug</a>
        </body>
    </html>
    """

@auth.route('/fix-login')
def fix_login():
    """Fix login issues by clearing session"""
    # Clear session
    session.clear()
    
    # Clear Flask-Login
    logout_user()
    
    flash('Session cleared. Please login again.', 'info')
    return redirect(url_for('auth.login'))