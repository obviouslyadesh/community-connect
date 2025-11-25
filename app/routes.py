from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
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
        # Using a free weather API (you can replace with OpenWeatherMap)
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
    # In a real app, you'd use Google Maps Embed API
    address_clean = address.replace(' ', '+')
    return f"https://maps.google.com/maps?q={address_clean}&output=embed"

@main.route('/')
def index():
    return render_template('index.html')

# @main.route('/dashboard')
# @login_required
# def dashboard():
#     if current_user.user_type == 'organization':
#         # Show organization's events and volunteers
#         events = Event.query.filter_by(organizer_id=current_user.id).all()
#         return render_template('dashboard.html', events=events)
#     else:
#         # Show volunteer's signed up events
#         signups = EventVolunteer.query.filter_by(volunteer_id=current_user.id).all()
#         events = [signup.event for signup in signups]
#         return render_template('dashboard.html', events=events)

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
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_event.html', form=form)

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
    
    # Check if already signed up
    existing_signup = EventVolunteer.query.filter_by(
        event_id=event_id, 
        volunteer_id=current_user.id
    ).first()
    
    if existing_signup:
        return jsonify({'error': 'Already signed up for this event'}), 400
    
    # Check if event is full
    if event.volunteers_count() >= event.max_volunteers:
        return jsonify({'error': 'Event is full'}), 400
    
    # Create signup
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
        # Show organization's events and volunteers
        events = Event.query.filter_by(organizer_id=current_user.id).all()
        return render_template('dashboard.html', events=events, now=datetime.utcnow())
    else:
        # Show volunteer's signed up events
        signups = EventVolunteer.query.filter_by(volunteer_id=current_user.id).all()
        events = [signup.event for signup in signups]
        return render_template('dashboard.html', events=events, now=datetime.utcnow())
    

# Admin routes
@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
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

@main.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@main.route('/admin/events')
@login_required
def admin_events():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
    events = Event.query.all()
    return render_template('admin_events.html', events=events)

@main.route('/admin/passwords')
@login_required
def admin_passwords():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin_passwords.html', users=users)

# API routes for admin actions
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

# Simple AI Chatbot using free API
@main.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        user_message = request.json.get('message', '')
        
        # Simple rule-based responses
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
    
    # Volunteer-related responses
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
    

@main.route('/admin/passwords-enhanced')
@login_required
def admin_passwords_enhanced():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin_passwords_enhanced.html', users=users)