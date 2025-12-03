from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('Account Type', choices=[('volunteer', 'Volunteer'), ('organization', 'Organization')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        # Import User inside method to avoid circular imports
        from app.models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        # Import User inside method to avoid circular imports
        from app.models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = StringField('Event Date & Time', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=300)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=20)])
    max_volunteers = IntegerField('Maximum Volunteers', default=10, 
                                  validators=[DataRequired(), NumberRange(min=1, max=100, message='Must be between 1 and 100')])
    submit = SubmitField('Create Event')
    
    def validate_date(self, date):
        """Validate that date is in the future"""
        try:
            event_datetime = datetime.strptime(date.data, '%Y-%m-%dT%H:%M')
            current_datetime = datetime.now()
            
            if event_datetime < current_datetime:
                raise ValidationError('Event date must be in the future. Please select a future date and time.')
        except ValueError:
            pass
    
    def validate_max_volunteers(self, max_volunteers):
        """Validate that max_volunteers is positive"""
        if max_volunteers.data <= 0:
            raise ValidationError('Maximum volunteers must be greater than 0.')