# app/auth.py - UPDATED WITH NEW FEATURES
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ChangeUsernameForm, ChangePasswordForm
from app.oauth import GoogleOAuth
from app.email import send_password_reset_email
import requests
import json
import secrets
from urllib.parse import urlencode
from app.models import User, PasswordResetToken

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Use remember parameter
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
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

# FORGOT PASSWORD FLOW
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate reset token
            token = user.generate_password_reset_token()
            
            # Send email
            send_password_reset_email(user, token)
            
            # Always show success message (security best practice)
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        else:
            # Still show success for security
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Verify token
    user = User.verify_password_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update password
        user.set_password(form.password.data)
        
        # Mark token as used
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token:
            reset_token.mark_as_used()
        
        db.session.commit()
        
        flash('Your password has been reset! You can now login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', form=form, token=token)

# USER PROFILE MANAGEMENT
@auth.route('/profile/change-username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    
    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.new_username.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken. Please choose another.', 'error')
            return render_template('change_username.html', form=form)
        
        # Update username
        old_username = current_user.username
        current_user.username = form.new_username.data
        db.session.commit()
        
        flash(f'Username changed from {old_username} to {current_user.username}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_username.html', form=form)

@auth.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html', form=form)
        
        # Update password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# GOOGLE OAUTH (Keep existing)
@auth.route('/auth/google')
def google_login():
    try:
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id or not redirect_uri:
            flash('OAuth not configured. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        
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
        return redirect(auth_url)
        
    except Exception as e:
        flash('Failed to connect to Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
@auth.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        tokens = GoogleOAuth.exchange_code_for_token(code)
        if not tokens or 'access_token' not in tokens:
            flash('Failed to get access token from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        user_info = GoogleOAuth.get_user_info(tokens['access_token'])
        if not user_info:
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.get_or_create_google_user(user_info)
        if not user:
            flash('Failed to create user account.', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=False)
        
        welcome_name = user_info.get('given_name') or user_info.get('name') or user.username
        flash(f'Welcome, {welcome_name}!', 'success')
        
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        flash(f'Failed to login with Google: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

# DEBUG ROUTES (Keep existing)
@auth.route('/debug/session')
def debug_session():
    from app.models import User
    
    current_user_info = {}
    if current_user.is_authenticated:
        current_user_info = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_authenticated': current_user.is_authenticated
        }
    else:
        current_user_info = {
            'is_authenticated': False,
            'id': 'Not logged in',
            'username': 'Not logged in',
            'email': 'Not logged in'
        }
    
    session_info = {
        'session_id': session.get('_id'),
        'user_id': session.get('user_id'),
        'user_email': session.get('user_email'),
        'oauth_state': session.get('oauth_state'),
        '_fresh': session.get('_fresh'),
        '_user_id': session.get('_user_id'),
        '_flashes': session.get('_flashes', [])
    }
    
    user_count = User.query.count()
    
    return f"""
    <html>
        <head><title>Session Debug</title></head>
        <body>
            <h1>Session Debug</h1>
            <h2>Session Info:</h2>
            <pre>{json.dumps(session_info, indent=2)}</pre>
            <h2>Current User:</h2>
            <pre>{json.dumps(current_user_info, indent=2)}</pre>
            <h2>Database Info:</h2>
            <p>Users in database: {user_count}</p>
            <h3>Test Links:</h3>
            <ul>
                <li><a href="/auth/google">Test Google Login</a></li>
                <li><a href="/debug/users">View All Users</a></li>
                <li><a href="/fix-session">Fix Session</a></li>
                <li><a href="/">Home</a></li>
                <li><a href="/dashboard">Dashboard</a></li>
            </ul>
        </body>
    </html>
    """

@auth.route('/debug/users')
def debug_users():
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
            <h1>Users in Database ({len(user_list)})</h1>
            <pre>{json.dumps(user_list, indent=2)}</pre>
            <hr>
            <a href="/debug/session">Session Debug</a> | 
            <a href="/">Home</a>
        </body>
    </html>
    """

@auth.route('/fix-session')
def fix_session():
    session.clear()
    logout_user()
    session.modified = True
    flash('Session cleared. Please login again.', 'info')
    return redirect(url_for('auth.login'))