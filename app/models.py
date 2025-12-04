# app/models.py - COMPLETE FIXED VERSION
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(20), nullable=False, default='volunteer')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Google OAuth fields
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    picture = db.Column(db.String(500), nullable=True)
    given_name = db.Column(db.String(64), nullable=True)
    family_name = db.Column(db.String(64), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_or_create_google_user(cls, google_data):
        """Get existing user by Google ID or create new one - FIXED"""
        from app import db
        
        print(f"\n🔄 get_or_create_google_user called")
        print(f"   Email: {google_data.get('email')}")
        print(f"   Google ID (sub): {google_data.get('sub')}")
        
        # Check if user exists by Google ID
        if 'sub' in google_data:
            user = cls.query.filter_by(google_id=google_data['sub']).first()
            if user:
                print(f"✅ Found existing user by Google ID: {user.email}")
                # Update user info if needed
                if google_data.get('picture') and not user.picture:
                    user.picture = google_data.get('picture')
                if google_data.get('given_name') and not user.given_name:
                    user.given_name = google_data.get('given_name')
                if google_data.get('family_name') and not user.family_name:
                    user.family_name = google_data.get('family_name')
                
                db.session.commit()
                return user
        
        # Check if user exists by email
        if 'email' in google_data:
            user = cls.query.filter_by(email=google_data['email']).first()
            if user:
                print(f"✅ Found existing user by email: {user.email}")
                # Link Google account to existing user
                if 'sub' in google_data:
                    user.google_id = google_data['sub']
                if google_data.get('picture') and not user.picture:
                    user.picture = google_data.get('picture')
                if google_data.get('given_name') and not user.given_name:
                    user.given_name = google_data.get('given_name')
                if google_data.get('family_name') and not user.family_name:
                    user.family_name = google_data.get('family_name')
                
                db.session.commit()
                return user
        
        # Create new user
        print(f"🔄 Creating new user for: {google_data.get('email')}")
        
        # Generate username from email
        email = google_data.get('email', '')
        if email:
            email_username = email.split('@')[0]
        else:
            email_username = 'google_user'
        
        username = email_username
        
        # Ensure username is unique
        counter = 1
        while cls.query.filter_by(username=username).first():
            username = f"{email_username}{counter}"
            counter += 1
        
        # Create user with available data
        user_data = {
            'username': username,
            'email': email,
            'user_type': 'volunteer'
        }
        
        if 'sub' in google_data:
            user_data['google_id'] = google_data['sub']
        if 'picture' in google_data:
            user_data['picture'] = google_data['picture']
        if 'given_name' in google_data:
            user_data['given_name'] = google_data['given_name']
        if 'family_name' in google_data:
            user_data['family_name'] = google_data['family_name']
        
        user = cls(**user_data)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Created new user: {user.username} (ID: {user.id})")
        return user
    
    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    __tablename__ = 'events'  # Changed from 'event' to be consistent
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    max_volunteers = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys - Fixed to reference 'users.id'
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    organizer = db.relationship('User', backref='organized_events')
    volunteers = db.relationship('EventVolunteer', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    def volunteers_count(self):
        return len(self.volunteers)
    
    def spots_remaining(self):
        return self.max_volunteers - self.volunteers_count()
    
    def can_edit(self, user):
        """Check if user can edit this event"""
        if not user.is_authenticated:
            return False
        return user.id == self.organizer_id or user.is_admin
    
    def can_delete(self, user):
        """Check if user can delete this event"""
        if not user.is_authenticated:
            return False
        return user.id == self.organizer_id or user.is_admin
    
    def __repr__(self):
        return f'<Event {self.title}>'

class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteers'  # Changed for consistency
    __table_args__ = (
        db.UniqueConstraint('event_id', 'volunteer_id', name='uq_volunteer_event'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    signed_up_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    volunteer = db.relationship('User', backref='volunteer_registrations')
    
    def __repr__(self):
        return f'<EventVolunteer event:{self.event_id} volunteer:{self.volunteer_id}>'
