from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Import db from app package

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    user_type = db.Column(db.String(20), nullable=True, default='volunteer')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Google OAuth fields
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    picture = db.Column(db.String(500), nullable=True)
    given_name = db.Column(db.String(80), nullable=True)
    family_name = db.Column(db.String(80), nullable=True)
    
    # Relationships
    events_created = db.relationship('Event', backref='organizer', lazy=True)
    volunteer_signups = db.relationship('EventVolunteer', backref='volunteer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_or_create_google_user(cls, google_data):
        """Get existing user or create new user from Google data"""
        # Check if user exists by google_id
        user = cls.query.filter_by(google_id=google_data['sub']).first()
        
        if not user:
            # Check if user exists by email
            user = cls.query.filter_by(email=google_data['email']).first()
            
            if user:
                # Update existing user with Google ID
                user.google_id = google_data['sub']
                user.picture = google_data.get('picture')
                user.given_name = google_data.get('given_name')
                user.family_name = google_data.get('family_name')
            else:
                # Create new user
                username = google_data['email'].split('@')[0]
                # Ensure username is unique
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
                    user_type='volunteer'
                )
                db.session.add(user)
        
        db.session.commit()
        return user
    
    def get_volunteer_stats(self):
        """Get volunteer statistics for admin view"""
        signups = EventVolunteer.query.filter_by(volunteer_id=self.id).all()
        completed_events = [s for s in signups if s.event.date < datetime.utcnow()]
        
        return {
            'total_events': len(signups),
            'completed_events': len(completed_events),
            'upcoming_events': len(signups) - len(completed_events),
            'first_event': min([s.signed_up_at for s in signups]) if signups else None
        }

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