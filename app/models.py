from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# class User(UserMixin, db.Model):
#     __tablename__ = 'user'
#     __table_args__ = {'extend_existing': True}  # ADD THIS LINE
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128))
#     user_type = db.Column(db.String(20), nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)  # Add admin field
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Relationships
#     events_created = db.relationship('Event', backref='organizer', lazy=True)
#     volunteer_signups = db.relationship('EventVolunteer', backref='volunteer', lazy=True)
    
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
    
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
    
#     def get_volunteer_stats(self):
#         """Get volunteer statistics for admin view"""
#         signups = EventVolunteer.query.filter_by(volunteer_id=self.id).all()
#         completed_events = [s for s in signups if s.event.date < datetime.utcnow()]
        
#         return {
#             'total_events': len(signups),
#             'completed_events': len(completed_events),
#             'upcoming_events': len(signups) - len(completed_events),
#             'first_event': min([s.signed_up_at for s in signups]) if signups else None
        # }

# class Event(db.Model):
#     __tablename__ = 'event'
#     __table_args__ = {'extend_existing': True}  # ADD THIS LINE
    
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     date = db.Column(db.DateTime, nullable=False)
#     address = db.Column(db.String(300), nullable=False)
#     city = db.Column(db.String(100), nullable=False)
#     state = db.Column(db.String(100), nullable=False)
#     zip_code = db.Column(db.String(20), nullable=False)
#     max_volunteers = db.Column(db.Integer, default=10)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Foreign Keys
#     organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
#     # Relationships
#     volunteers = db.relationship('EventVolunteer', backref='event', lazy=True, cascade='all, delete-orphan')
    
#     def get_full_address(self):
#         return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
#     def volunteers_count(self):
#         return len(self.volunteers)
    
#     def spots_remaining(self):
#         return self.max_volunteers - self.volunteers_count()
    
# #edit and delete option
#     def can_edit(self, user):
#         """Check if user can edit this event"""
#         return user.is_authenticated and (user.id == self.organizer_id or user.is_admin)
    
#     def can_delete(self, user):
#         """Check if user can delete this event"""
#         return user.is_authenticated and (user.id == self.organizer_id or user.is_admin)

class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteer'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'volunteer_id', name='unique_volunteer_event'),
        {'extend_existing': True}  # ADD THIS LINE
    )
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    signed_up_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # DEVELOPMENT ONLY: Store plain text password (NEVER in production!)
    plain_password = db.Column(db.String(128))
    
    user_type = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events_created = db.relationship('Event', backref='organizer', lazy=True)
    volunteer_signups = db.relationship('EventVolunteer', backref='volunteer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
        # DEVELOPMENT ONLY: Store plain text if developer mode is enabled
        from flask import current_app
        if current_app.config.get('DEVELOPER_MODE', False):
            self.plain_password = password
        else:
            self.plain_password = None  # Don't store in production
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_plain_password(self):
        """Get plain text password (DEVELOPMENT ONLY)"""
        from flask import current_app
        if current_app.config.get('DEVELOPER_MODE', False) and self.plain_password:
            return self.plain_password
        return "🔒 Password hidden (Developer mode disabled)"
    
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
    
    # ADD THESE METHODS:
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