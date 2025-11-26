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

# @main.route('/events/create', methods=['GET', 'POST'])
# @login_required
# def create_event():
#     if current_user.user_type != 'organization':
#         flash('Only organizations can create events.', 'warning')
#         return redirect(url_for('main.events'))
    
#     form = EventForm()
#     if form.validate_on_submit():
#         event = Event(
#             title=form.title.data,
#             description=form.description.data,
#             date=form.date.data,
#             address=form.address.data,
#             city=form.city.data,
#             state=form.state.data,
#             zip_code=form.zip_code.data,
#             max_volunteers=form.max_volunteers.data,
#             organizer_id=current_user.id
#         )
#         db.session.add(event)
#         db.session.commit()
#         flash('Event created successfully!', 'success')
#         return redirect(url_for('main.dashboard'))
    
#     return render_template('create_event.html', form=form)

@main.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.user_type != 'organization':
        flash('Only organizations can create events.', 'warning')
        return redirect(url_for('main.events'))
    
    form = EventForm()
    
    if form.validate_on_submit():
        try:
            # Debug: Print form data
            print(f"Form data: {form.data}")
            
            # Parse datetime from string
            from datetime import datetime
            event_date = datetime.strptime(form.date.data, '%Y-%m-%dT%H:%M')
            
            # Create event
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

# @main.route('/admin/events')
# @login_required
# def admin_events():
#     if not current_user.is_admin:
#         flash('Admin access required', 'error')
#         return redirect(url_for('main.dashboard'))
    
#     events = Event.query.all()
#     return render_template('admin_events.html', events=events)

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

# @main.route('/debug-db')
# def debug_database():
#     from app import db
#     from app.models import User
#     import os
    
#     try:
#         # Test connection
#         db.session.execute('SELECT 1')
#         db_status = '✅ CONNECTED'
        
#         # Get user count
#         user_count = User.query.count()
#         users = User.query.all()
        
#         user_list = ""
#         for user in users:
#             user_list += f"<li>{user.username} ({user.email}) - {user.user_type}</li>"
        
#     except Exception as e:
#         db_status = f'❌ ERROR: {str(e)}'
#         user_count = 'N/A'
#         user_list = ''
    
#     db_url = os.environ.get('DATABASE_URL', 'Not found')
    
#     return f"""
#     <h2>Database Debug</h2>
#     <p><strong>Database URL:</strong> {db_url[:50]}...</p>
#     <p><strong>Status:</strong> {db_status}</p>
#     <p><strong>Total Users:</strong> {user_count}</p>
#     <p><strong>Existing Users:</strong></p>
#     <ul>{user_list}</ul>
#     <p><a href="/register">Register New User</a></p>
#     """


@main.route('/debug-events')
def debug_events():
    from app.models import Event, User
    from app import db
    
    try:
        events = Event.query.all()
        users = User.query.all()
        
        events_info = ""
        for event in events:
            events_info += f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
                <strong>{event.title}</strong><br>
                ID: {event.id} | Organizer: {event.organizer.username}<br>
                Date: {event.date} | Volunteers: {event.volunteers_count()}/{event.max_volunteers}
            </div>
            """
        
        users_info = ""
        for user in users:
            users_info += f"<li>{user.username} ({user.user_type}) - ID: {user.id}</li>"
        
        return f"""
        <h2>Events Debug</h2>
        <h3>Existing Events ({len(events)}):</h3>
        {events_info if events else '<p>No events found</p>'}
        
        <h3>Existing Users ({len(users)}):</h3>
        <ul>{users_info}</ul>
        
        <h3>Actions:</h3>
        <a href="/events/create" class="btn btn-primary">Create Event</a>
        <a href="/debug-db" class="btn btn-secondary">Database Debug</a>
        """
        
    except Exception as e:
        return f"<h2>Error</h2><p>{str(e)}</p>"

@main.route('/debug-create-test-event')
@login_required
def debug_create_test_event():
    from app.models import Event
    from datetime import datetime, timedelta
    
    try:
        # Create a test event
        test_event = Event(
            title="Test Event - Debug",
            description="This is a test event created for debugging",
            date=datetime.utcnow() + timedelta(days=1),
            address="123 Test Street",
            city="Test City",
            state="TS",
            zip_code="12345",
            max_volunteers=5,
            organizer_id=current_user.id
        )
        
        db.session.add(test_event)
        db.session.commit()
        
        return f"""
        <h2>Test Event Created Successfully!</h2>
        <p>Event: {test_event.title}</p>
        <p>Organizer: {current_user.username}</p>
        <p><a href="/debug-events">View All Events</a></p>
        """
        
    except Exception as e:
        return f"<h2>Error Creating Test Event</h2><p>{str(e)}</p>"
    
@main.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check permissions
    if not event.can_edit(current_user):
        flash('You do not have permission to edit this event.', 'error')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    form = EventForm()
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date.strftime('%Y-%m-%dT%H:%M')  # Format for datetime-local
        form.address.data = event.address
        form.city.data = event.city
        form.state.data = event.state
        form.zip_code.data = event.zip_code
        form.max_volunteers.data = event.max_volunteers
    
    if form.validate_on_submit():
        try:
            # Update event
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
    
    # Check permissions
    if not event.can_delete(current_user):
        flash('You do not have permission to delete this event.', 'error')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    try:
        # Delete the event (cascade should handle volunteer signups)
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting event: {str(e)}', 'error')
    
    # Redirect to appropriate page
    if current_user.user_type == 'organization':
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.events'))
    
@main.route('/admin/events')
@login_required
def admin_events():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('main.dashboard'))
    
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('admin_events.html', events=events)

@main.route('/debug-users')
def debug_users():
    from app.models import User
    from app import db
    
    try:
        users = User.query.all()
        user_list = ""
        for user in users:
            admin_status = " (ADMIN)" if user.is_admin else ""
            user_list += f"<li>{user.username}{admin_status} - {user.email} - {user.user_type}</li>"
        
        return f"""
        <h2>Current Users in Database</h2>
        <ul>{user_list if users else 'No users found'}</ul>
        <p><a href="/register">Register New User</a></p>
        <p><a href="/debug-db">Database Info</a></p>
        """
    except Exception as e:
        return f"<h2>Error</h2><p>{str(e)}</p>"
    
@main.route('/reset-user-password/<username>/<new_password>')
def reset_user_password(username, new_password):
    """Emergency password reset (use carefully!)"""
    from app.models import User
    
    # Simple security - change this key
    secret_key = request.args.get('key', '')
    if secret_key != 'emergency2024':
        return "Invalid access", 403
    
    user = User.query.filter_by(username=username).first()
    if user:
        user.set_password(new_password)
        db.session.commit()
        return f"✅ Password reset for {username} to: {new_password}"
    else:
        return f"❌ User {username} not found"