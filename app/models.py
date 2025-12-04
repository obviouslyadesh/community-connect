from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Import db from app package

# app/models.py - UPDATED VERSION
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Changed from 'user' to avoid conflicts
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(20), nullable=False, default='volunteer')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Google OAuth fields
    google_id = db.Column(db.String(120), unique=True, nullable=True)  # ADD THIS
    picture = db.Column(db.String(500), nullable=True)  # ADD THIS
    given_name = db.Column(db.String(64), nullable=True)  # ADD THIS
    family_name = db.Column(db.String(64), nullable=True)  # ADD THIS
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_or_create_google_user(cls, google_data):
        """Get existing user by Google ID or create new one"""
        # Check if user exists by Google ID
        user = cls.query.filter_by(google_id=google_data['sub']).first()
        
        if user:
            # Update user info if needed
            user.email = google_data.get('email', user.email)
            user.picture = google_data.get('picture', user.picture)
            user.given_name = google_data.get('given_name', user.given_name)
            user.family_name = google_data.get('family_name', user.family_name)
            return user
        
        # Check if user exists by email (in case they signed up manually first)
        user = cls.query.filter_by(email=google_data['email']).first()
        if user:
            # Link Google account to existing user
            user.google_id = google_data['sub']
            user.picture = google_data.get('picture')
            user.given_name = google_data.get('given_name')
            user.family_name = google_data.get('family_name')
            return user
        
        # Create new user
        username = google_data.get('email', '').split('@')[0]
        # Make sure username is unique
        base_username = username
        counter = 1
        while cls.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = cls(
            username=username,
            email=google_data['email'],
            google_id=google_data['sub'],
            picture=google_data.get('picture'),
            given_name=google_data.get('given_name'),
            family_name=google_data.get('family_name'),
            user_type='volunteer'  # Default to volunteer
        )
        
        db.session.add(user)
        return user
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    __tablename__ = 'event'
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
    
    # Foreign Keys
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
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

class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteer'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'volunteer_id', name='unique_volunteer_event'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    signed_up_at = db.Column(db.DateTime, default=datetime.utcnow)