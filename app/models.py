# app/models.py - UPDATED WITH PASSWORD RESET TOKENS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import secrets
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
    
    # Relationships
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_password_reset_token(self):
        """Generate a password reset token"""
        # Invalidate any existing tokens
        PasswordResetToken.query.filter_by(user_id=self.id).delete()
        
        # Create new token
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            token=token,
            user_id=self.id,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        )
        db.session.add(reset_token)
        db.session.commit()
        return token
    
    @staticmethod
    def verify_password_reset_token(token):
        """Verify a password reset token"""
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if reset_token and reset_token.is_valid():
            return reset_token.user
        return None
    
    @classmethod
    def get_or_create_google_user(cls, google_data):
        """Get existing user by Google ID or create new one"""
        from app import db
        
        # Check if user exists by Google ID
        if 'sub' in google_data:
            user = cls.query.filter_by(google_id=google_data['sub']).first()
            if user:
                return user
        
        # Check if user exists by email
        if 'email' in google_data:
            user = cls.query.filter_by(email=google_data['email']).first()
            if user:
                # Link Google account to existing user
                if 'sub' in google_data:
                    user.google_id = google_data['sub']
                db.session.commit()
                return user
        
        # Create new user
        email = google_data.get('email', '')
        email_username = email.split('@')[0] if email else 'google_user'
        username = email_username
        
        # Ensure username is unique
        counter = 1
        while cls.query.filter_by(username=username).first():
            username = f"{email_username}{counter}"
            counter += 1
        
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
        return user
    
    def __repr__(self):
        return f'<User {self.username}>'


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        """Check if token is still valid"""
        return (not self.used) and (datetime.utcnow() < self.expires_at)
    
    def mark_as_used(self):
        """Mark token as used"""
        self.used = True
        db.session.commit()


class Event(db.Model):
    __tablename__ = 'events'
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
    
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    organizer = db.relationship('User', backref='organized_events')
    volunteers = db.relationship('EventVolunteer', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    def volunteers_count(self):
        return len(self.volunteers)
    
    def spots_remaining(self):
        return self.max_volunteers - self.volunteers_count()
    
    def can_edit(self, user):
        if not user.is_authenticated:
            return False
        return user.id == self.organizer_id or user.is_admin
    
    def can_delete(self, user):
        if not user.is_authenticated:
            return False
        return user.id == self.organizer_id or user.is_admin
    
    def __repr__(self):
        return f'<Event {self.title}>'


class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteers'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'volunteer_id', name='uq_volunteer_event'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    signed_up_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    volunteer = db.relationship('User', backref='volunteer_registrations')
    
    def __repr__(self):
        return f'<EventVolunteer event:{self.event_id} volunteer:{self.volunteer_id}>'