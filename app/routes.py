from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import Event, User, EventVolunteer
from app.forms import EventForm
import requests
from datetime import datetime
import json


main = Blueprint('main', __name__)

# External API functions
def get_weather_forecast(city):
    """Get weather forecast using OpenWeatherMap API"""
    try:
        url = f"http://wttr.in/{city}?format=j1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_condition = data['current_condition'][0]
            return {
                'temp': current_condition['temp_C'],
                'desc': current_condition['weatherDesc'][0]['value'],
                'humidity': current_condition['humidity']
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None

def get_map_embed_url(address):
    """Generate Google Maps embed URL"""
    address_clean = address.replace(' ', '+')
    return f"https://maps.google.com/maps?q={address_clean}&output=embed"

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/events')
def events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).paginate(page=page, per_page=6)
    return render_template('events.html', events=events)

@main.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.user_type != 'organization':
        flash('Only organizations can create events.', 'warning')
        return redirect(url_for('main.events'))
    
    form = EventForm()
    
    # Calculate minimum date (5 minutes from now)
    from datetime import datetime, timedelta
    min_date = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M')
    
    if form.validate_on_submit():
        try:
            print(f"Form data: {form.data}")
            
            event_date = datetime.strptime(form.date.data, '%Y-%m-%dT%H:%M')
            
            # Additional validation in route
            if event_date < datetime.now():
                flash('Event date must be in the future.', 'error')
                return render_template('create_event.html', form=form, min_date=min_date)
            
            if form.max_volunteers.data < 1:
                flash('Maximum volunteers must be at least 1.', 'error')
                return render_template('create_event.html', form=form, min_date=min_date)
            
            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=event_date,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zip_code=form.zip_code.data,
                max_volunteers=form.max_volunteers.data,
                organizer_id=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash('Event created successfully!', 'success')
            print(f"Event created: {event.title} by {current_user.username}")
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'error')
            print(f"Event creation error: {e}")
    
    elif form.errors:
        print(f"Form errors: {form.errors}")
        flash('Please correct the errors in the form.', 'error')
    
    return render_template('create_event.html', form=form, min_date=min_date)

@main.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    weather = get_weather_forecast(event.city)
    map_url = get_map_embed_url(event.get_full_address())
    is_signed_up = False
    
    if current_user.is_authenticated and current_user.user_type == 'volunteer':
        is_signed_up = EventVolunteer.query.filter_by(
            event_id=event_id, 
            volunteer_id=current_user.id
        ).first() is not None
    
    return render_template('event_detail.html', 
                         event=event, 
                         weather=weather, 
                         map_url=map_url,
                         is_signed_up=is_signed_up)

# API Routes
@main.route('/api/events', methods=['GET'])
def api_get_events():
    events = Event.query.filter(Event.date >= datetime.utcnow()).all()
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat(),
            'location': event.get_full_address(),
            'organizer': event.organizer.username,
            'volunteers_count': event.volunteers_count(),
            'max_volunteers': event.max_volunteers
        })
    return jsonify(events_data)

@main.route('/api/events', methods=['POST'])
@login_required
def api_create_event():
    if current_user.user_type != 'organization':
        return jsonify({'error': 'Only organizations can create events'}), 403
    
    data = request.get_json()
    event = Event(
        title=data['title'],
        description=data['description'],
        date=datetime.fromisoformat(data['date']),
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        max_volunteers=data.get('max_volunteers', 10),
        organizer_id=current_user.id
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event created successfully', 'event_id': event.id}), 201

@main.route('/api/events/<int:event_id>/volunteer', methods=['POST'])
@login_required
def api_volunteer_signup(event_id):
    if current_user.user_type != 'volunteer':
        return jsonify({'error': 'Only volunteers can sign up for events'}), 403
    
    event = Event.query.get_or_404(event_id)
    
    existing_signup = EventVolunteer.query.filter_by(
        event_id=event_id, 
        volunteer_id=current_user.id
    ).first()
    
    if existing_signup:
        return jsonify({'error': 'Already signed up for this event'}), 400
    
    if event.volunteers_count() >= event.max_volunteers:
        return jsonify({'error': 'Event is full'}), 400
    
    signup = EventVolunteer(event_id=event_id, volunteer_id=current_user.id)
    db.session.add(signup)
    db.session.commit()
    
    return jsonify({'message': 'Successfully signed up for event'}), 201

@main.route('/api/events/<int:event_id>/volunteer', methods=['DELETE'])
@login_required
def api_volunteer_cancel(event_id):
    signup = EventVolunteer.query.filter_by(
        event_id=event_id, 
        volunteer_id=current_user.id
    ).first_or_404()
    
    db.session.delete(signup)
    db.session.commit()
    
    return jsonify({'message': 'Successfully canceled event signup'}), 200

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'organization':
        events = Event.query.filter_by(organizer_id=current_user.id).all()
        return render_template('dashboard.html', events=events, now=datetime.utcnow())
    else:
        signups = EventVolunteer.query.filter_by(volunteer_id=current_user.id).all()
        events = [signup.event for signup in signups]
        return render_template('dashboard.html', events=events, now=datetime.utcnow())

# =================== NEW ADMIN LOGIN SYSTEM ===================
@main.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin-only login page at /admin"""
    # If already logged in as admin, redirect to admin dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))
    
    # If logged in but not admin, logout first
    if current_user.is_authenticated and not current_user.is_admin:
        logout_user()
        flash('Please login with admin credentials to access admin console.', 'info')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_admin:
                login_user(user)
                flash('Admin login successful!', 'success')
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('This account does not have admin privileges.', 'error')
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard - only accessible by admins"""
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.admin_login'))
    
    # Admin statistics
    total_users = User.query.count()
    total_events = Event.query.count()
    total_volunteers = User.query.filter_by(user_type='volunteer').count()
    total_organizations = User.query.filter_by(user_type='organization').count()
    recent_signups = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_events=total_events,
                         total_volunteers=total_volunteers,
                         total_organizations=total_organizations,
                         recent_signups=recent_signups)

@main.route('/admin/logout')
@login_required
def admin_logout():
    """Logout from admin console"""
    logout_user()
    flash('Admin logout successful.', 'info')
    return redirect(url_for('main.index'))

# =================== ADMIN MANAGEMENT ROUTES ===================
@main.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.admin_login'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@main.route('/admin/events')
@login_required
def admin_events():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.admin_login'))
    
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('admin_events.html', events=events)


# =================== ADMIN API ROUTES ===================
@main.route('/api/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def api_toggle_admin(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'message': f'Admin status updated for {user.username}',
        'is_admin': user.is_admin
    })

@main.route('/api/admin/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's data
    Event.query.filter_by(organizer_id=user_id).delete()
    EventVolunteer.query.filter_by(volunteer_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': f'User {user.username} deleted successfully'})

# =================== CHATBOT ===================
@main.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        user_message = request.json.get('message', '')
        response = generate_chatbot_response(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Chatbot unavailable'}), 500

def generate_chatbot_response(message):
    """Generate responses based on common volunteer-related questions"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your volunteer assistant. How can I help you with volunteering today?"
    
    elif any(word in message_lower for word in ['event', 'opportunity']):
        return "You can browse all available events on the Events page. Organizations post events where they need volunteers like you!"
    
    elif any(word in message_lower for word in ['sign up', 'register', 'join']):
        return "To sign up for an event, just go to the event details page and click 'Sign Up as Volunteer'. You need to be logged in first!"
    
    elif any(word in message_lower for word in ['create', 'organize', 'host']):
        return "To create an event, you need an organization account. Register as an organization to post volunteer opportunities!"
    
    elif any(word in message_lower for word in ['weather', 'rain', 'sunny']):
        return "I check weather for each event! Visit any event page to see weather forecasts and preparation tips."
    
    elif any(word in message_lower for word in ['cancel', 'remove']):
        return "To cancel your volunteer signup, go to your Dashboard and click 'Cancel' next to the event."
    
    elif any(word in message_lower for word in ['help', 'support']):
        return "I can help you with: finding events, signing up, event creation, weather info, and account questions. What do you need?"
    
    else:
        return "I'm here to help with volunteering! You can ask me about events, signing up, creating events, or weather information. What would you like to know?"

# =================== EVENT MANAGEMENT ===================
@main.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if not event.can_edit(current_user):
        flash('You do not have permission to edit this event.', 'error')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    form = EventForm()
    
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date.strftime('%Y-%m-%dT%H:%M')
        form.address.data = event.address
        form.city.data = event.city
        form.state.data = event.state
        form.zip_code.data = event.zip_code
        form.max_volunteers.data = event.max_volunteers
    
    if form.validate_on_submit():
        try:
            event.title = form.title.data
            event.description = form.description.data
            event.date = datetime.strptime(form.date.data, '%Y-%m-%dT%H:%M')
            event.address = form.address.data
            event.city = form.city.data
            event.state = form.state.data
            event.zip_code = form.zip_code.data
            event.max_volunteers = form.max_volunteers.data
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('main.event_detail', event_id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'error')
    
    return render_template('edit_event.html', form=form, event=event)

@main.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if not event.can_delete(current_user):
        flash('You do not have permission to delete this event.', 'error')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting event: {str(e)}', 'error')
    
    if current_user.user_type == 'organization':
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.events'))
    
@main.route('/test-google-oauth')
def test_google_oauth():
    """Direct test of Google OAuth URL generation"""
    from urllib.parse import urlencode
    import secrets
    
    # Clickable link
    client_id = "329204650680-0rmc3npi3a3kf1o3cocr4n56dd0so8o3.apps.googleusercontent.com"
    redirect_uri = "https://community-connect-project.onrender.com/auth/google/callback"
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
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return f"""
    <html>
    <head><title>Google OAuth Test</title></head>
    <body>
        <h1>Google OAuth Test</h1>
        <p>This URL should work:</p>
        <a href="{auth_url}" target="_blank" style="font-size: 14px; word-break: break-all;">
            {auth_url[:100]}...
        </a>
        <br><br>
        <a href="{auth_url}" target="_blank">
            <button>Test Google Login</button>
        </a>
        <br><br>
        <p>If this works but /auth/google doesn't, there's an issue in auth.py</p>
        <p><a href="/auth/google">Test regular auth/google route</a></p>
    </body>
    </html>
    """